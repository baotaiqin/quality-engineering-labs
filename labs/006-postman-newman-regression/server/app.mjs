import http from "node:http";
import { randomBytes } from "node:crypto";
import { pathToFileURL } from "node:url";

export class AuthStore {
  constructor() {
    this.users = new Map();
    this.tokens = new Map();
  }

  createUser(username, password) {
    if (this.users.has(username)) {
      return false;
    }
    this.users.set(username, password);
    return true;
  }

  login(username, password) {
    if (this.users.get(username) !== password) {
      return null;
    }
    const token = randomBytes(24).toString("base64url");
    this.tokens.set(token, username);
    return token;
  }

  usernameForToken(token) {
    return this.tokens.get(token) ?? null;
  }

  revoke(token) {
    this.tokens.delete(token);
  }
}

function json(response, statusCode, body, headers = {}) {
  const content = JSON.stringify(body);
  response.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(content),
    ...headers,
  });
  response.end(content);
}

function empty(response, statusCode) {
  response.writeHead(statusCode);
  response.end();
}

async function readJson(request) {
  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }
  if (chunks.length === 0) {
    return {};
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function bearerToken(request) {
  const authorization = request.headers.authorization ?? "";
  return authorization.startsWith("Bearer ")
    ? authorization.slice("Bearer ".length)
    : null;
}

export function createAuthServer(store = new AuthStore()) {
  return http.createServer(async (request, response) => {
    const url = new URL(request.url, "http://127.0.0.1");

    try {
      if (request.method === "GET" && url.pathname === "/health") {
        return json(response, 200, { status: "ok" });
      }

      if (request.method === "POST" && url.pathname === "/api/users") {
        const body = await readJson(request);
        if (!body.username || !body.password) {
          return json(response, 422, {
            code: "VALIDATION_ERROR",
            message: "username和password不能为空",
          });
        }
        if (!store.createUser(body.username, body.password)) {
          return json(response, 409, {
            code: "USER_EXISTS",
            message: "用户名已存在",
          });
        }
        return json(response, 201, {
          username: body.username,
          status: "active",
        });
      }

      if (request.method === "POST" && url.pathname === "/api/login") {
        const body = await readJson(request);
        if (!body.username || !body.password) {
          return json(response, 422, {
            code: "VALIDATION_ERROR",
            message: "username和password不能为空",
          });
        }
        const token = store.login(body.username, body.password);
        if (!token) {
          return json(
            response,
            401,
            { code: "INVALID_CREDENTIALS", message: "用户名或密码错误" },
            { "www-authenticate": "Bearer" },
          );
        }
        return json(response, 200, {
          access_token: token,
          token_type: "bearer",
          expires_in: 3600,
        });
      }

      if (request.method === "GET" && url.pathname === "/api/profile") {
        const token = bearerToken(request);
        const username = token ? store.usernameForToken(token) : null;
        if (!username) {
          return json(
            response,
            401,
            { code: "TOKEN_INVALID", message: "Token无效或已失效" },
            { "www-authenticate": "Bearer" },
          );
        }
        return json(response, 200, { username, status: "active" });
      }

      if (request.method === "POST" && url.pathname === "/api/logout") {
        const token = bearerToken(request);
        const username = token ? store.usernameForToken(token) : null;
        if (!username) {
          return json(
            response,
            401,
            { code: "TOKEN_INVALID", message: "Token无效或已失效" },
            { "www-authenticate": "Bearer" },
          );
        }
        store.revoke(token);
        return empty(response, 204);
      }

      return json(response, 404, {
        code: "NOT_FOUND",
        message: "接口不存在",
      });
    } catch (error) {
      return json(response, 400, {
        code: "INVALID_JSON",
        message: "请求体不是有效JSON",
      });
    }
  });
}

export function listen(server, port = 3100) {
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, "127.0.0.1", () => {
      server.off("error", reject);
      resolve(server.address());
    });
  });
}

export function close(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

const isMain = process.argv[1]
  && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  const server = createAuthServer();
  const port = Number(process.env.PORT ?? 3100);
  await listen(server, port);
  console.log(`Local Auth API: http://127.0.0.1:${port}`);
}
