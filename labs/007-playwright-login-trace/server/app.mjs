import http from 'node:http';
import { randomUUID } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const sessions = new Map();
const account = { username: 'reader', password: 'local-pass-2026', displayName: 'reader' };

async function serveFile(response, fileName, contentType) {
  const body = await readFile(path.join(here, 'public', fileName));
  response.writeHead(200, { 'content-type': contentType, 'content-length': body.length });
  response.end(body);
}

function sendJson(response, status, data) {
  const body = JSON.stringify(data);
  response.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(body),
  });
  response.end(body);
}

function sessionId(request) {
  const match = /(?:^|;\s*)sid=([^;]+)/.exec(request.headers.cookie ?? '');
  return match?.[1] ?? null;
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}

export function createServer() {
  return http.createServer(async (request, response) => {
    const url = new URL(request.url, 'http://127.0.0.1');

    try {
      if (request.method === 'GET' && url.pathname === '/health') {
        return sendJson(response, 200, { status: 'ok' });
      }
      if (request.method === 'GET' && url.pathname === '/app.css') {
        return serveFile(response, 'app.css', 'text/css; charset=utf-8');
      }
      if (request.method === 'GET' && url.pathname === '/login') {
        return serveFile(response, 'login.html', 'text/html; charset=utf-8');
      }
      if (request.method === 'GET' && url.pathname === '/dashboard') {
        const sid = sessionId(request);
        if (!sid || !sessions.has(sid)) {
          response.writeHead(302, { location: '/login' });
          return response.end();
        }
        return serveFile(response, 'dashboard.html', 'text/html; charset=utf-8');
      }
      if (request.method === 'GET' && url.pathname === '/') {
        response.writeHead(302, { location: '/login' });
        return response.end();
      }
      if (request.method === 'POST' && url.pathname === '/api/session') {
        const body = await readBody(request);
        await new Promise((resolve) => setTimeout(resolve, 240));
        if (body.username !== account.username || body.password !== account.password) {
          return sendJson(response, 401, { code: 'INVALID_CREDENTIALS', message: '用户名或密码错误' });
        }
        const sid = randomUUID();
        sessions.set(sid, account.displayName);
        response.setHeader('set-cookie', `sid=${sid}; HttpOnly; SameSite=Lax; Path=/`);
        return sendJson(response, 200, { displayName: account.displayName });
      }
      if (request.method === 'GET' && url.pathname === '/api/session') {
        const sid = sessionId(request);
        if (!sid || !sessions.has(sid)) {
          return sendJson(response, 401, { code: 'UNAUTHENTICATED' });
        }
        return sendJson(response, 200, { displayName: sessions.get(sid) });
      }
      if (request.method === 'DELETE' && url.pathname === '/api/session') {
        const sid = sessionId(request);
        if (sid) sessions.delete(sid);
        response.setHeader('set-cookie', 'sid=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/');
        response.writeHead(204);
        return response.end();
      }
      return sendJson(response, 404, { code: 'NOT_FOUND' });
    } catch (error) {
      return sendJson(response, 400, { code: 'INVALID_REQUEST' });
    }
  });
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;
if (isMain) {
  const port = Number(process.env.PORT ?? 4174);
  createServer().listen(port, '127.0.0.1', () => {
    console.log(`Login web app: http://127.0.0.1:${port}/login`);
  });
}
