import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Dependency-free fallback target for local SentinelAPI demonstrations.
 * It intentionally exposes one vulnerable and one secure resource endpoint.
 */
public class Main {
    private static final Pattern USERNAME = Pattern.compile("\"username\"\\s*:\\s*\"([^\"]+)\"");

    public static void main(String[] args) throws Exception {
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "8090"));
        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", port), 0);
        server.createContext("/openapi.json", Main::openapi);
        server.createContext("/auth/login", Main::login);
        server.createContext("/api/vulnerable/users/1", exchange -> user(exchange, false));
        server.createContext("/api/secure/users/1", exchange -> user(exchange, true));
        server.start();
        System.out.println("Fallback target listening on http://127.0.0.1:" + port);
    }

    private static void openapi(HttpExchange exchange) throws IOException {
        String body = """
            {"openapi":"3.0.0","info":{"title":"SentinelAPI fallback target","version":"1.0"},
             "paths":{
              "/api/vulnerable/users/{id}":{"get":{"responses":{"200":{"description":"user"}}}},
              "/api/secure/users/{id}":{"get":{"responses":{"200":{"description":"user"}}}}
             }}
            """;
        json(exchange, 200, body);
    }

    private static void login(HttpExchange exchange) throws IOException {
        String input = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        Matcher matcher = USERNAME.matcher(input);
        String username = matcher.find() ? matcher.group(1) : "";
        if (!username.equals("alice") && !username.equals("bob")) {
            json(exchange, 401, "{\"error\":\"invalid credentials\"}");
            return;
        }
        json(exchange, 200, "{\"token\":\"" + username + "-demo-token\"}");
    }

    private static void user(HttpExchange exchange, boolean secure) throws IOException {
        String authorization = exchange.getRequestHeaders().getFirst("Authorization");
        String username = authorization != null && authorization.contains("alice") ? "alice" : "bob";
        if (secure && !username.equals("alice")) {
            json(exchange, 403, "{\"error\":\"forbidden\"}");
            return;
        }
        String body = "{\"id\":1,\"username\":\"alice\",\"email\":\"alice@example.test\",\"password_hash\":\"demo-only\"}";
        json(exchange, 200, body);
    }

    private static void json(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream output = exchange.getResponseBody()) {
            output.write(bytes);
        }
    }
}
