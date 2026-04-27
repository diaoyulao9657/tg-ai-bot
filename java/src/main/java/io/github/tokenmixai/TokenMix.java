package io.github.tokenmixai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Java client for TokenMix.
 *
 * <p>One API key for GPT-5, Claude, Gemini, DeepSeek and 155+ LLMs through a
 * single OpenAI-compatible endpoint.</p>
 *
 * <p>Get a free API key at <a href="https://tokenmix.ai">https://tokenmix.ai</a>.</p>
 *
 * <pre>{@code
 * TokenMix client = new TokenMix(System.getenv("TOKENMIX_API_KEY"));
 * String reply = client.chat("gpt-5", List.of(
 *     new TokenMix.Message("user", "Hello!")
 * ));
 * System.out.println(reply);
 * }</pre>
 */
public class TokenMix {
    public static final String DEFAULT_BASE_URL = "https://api.tokenmix.ai/v1";

    private final String apiKey;
    private final String baseUrl;
    private final HttpClient http;
    private final ObjectMapper json = new ObjectMapper();

    public TokenMix(String apiKey) {
        this(apiKey, DEFAULT_BASE_URL);
    }

    public TokenMix(String apiKey, String baseUrl) {
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("apiKey is required");
        }
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.http = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();
    }

    /** A chat message (role: "user" / "assistant" / "system"). */
    public static class Message {
        public final String role;
        public final String content;

        public Message(String role, String content) {
            this.role = role;
            this.content = content;
        }

        public String getRole() { return role; }
        public String getContent() { return content; }
    }

    /**
     * Send a chat completion request and return the assistant reply.
     *
     * @param model    model name, e.g. "gpt-5", "claude-opus-4-5", "deepseek-v3"
     * @param messages list of messages
     * @return the assistant's reply text
     * @throws Exception on HTTP error or invalid response
     */
    public String chat(String model, List<Message> messages) throws Exception {
        ObjectNode body = json.createObjectNode();
        body.put("model", model);
        ArrayNode arr = body.putArray("messages");
        for (Message m : messages) {
            ObjectNode node = arr.addObject();
            node.put("role", m.role);
            node.put("content", m.content);
        }

        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/chat/completions"))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(60))
                .POST(HttpRequest.BodyPublishers.ofString(json.writeValueAsString(body)))
                .build();

        HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() >= 400) {
            throw new RuntimeException("TokenMix API error: HTTP " + resp.statusCode() + ": " + resp.body());
        }

        JsonNode data = json.readTree(resp.body());
        return data.path("choices").path(0).path("message").path("content").asText("");
    }

    /**
     * List available model IDs.
     *
     * @return list of model IDs
     * @throws Exception on HTTP error or invalid response
     */
    public List<String> listModels() throws Exception {
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/models"))
                .header("Authorization", "Bearer " + apiKey)
                .timeout(Duration.ofSeconds(30))
                .GET()
                .build();

        HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() >= 400) {
            throw new RuntimeException("TokenMix API error: HTTP " + resp.statusCode() + ": " + resp.body());
        }

        JsonNode data = json.readTree(resp.body());
        List<String> ids = new ArrayList<>();
        JsonNode arr = data.path("data");
        if (arr.isArray()) {
            for (JsonNode node : arr) {
                String id = node.path("id").asText();
                if (!id.isEmpty()) ids.add(id);
            }
        }
        return ids;
    }
}
