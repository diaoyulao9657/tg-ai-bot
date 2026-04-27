# TokenMix Java Client

[![Maven Central](https://img.shields.io/maven-central/v/io.github.tokenmixai/tokenmix-client.svg)](https://central.sonatype.com/artifact/io.github.tokenmixai/tokenmix-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by TokenMix](https://img.shields.io/badge/Powered%20by-TokenMix.ai-blue)](https://tokenmix.ai)

> Java client for [TokenMix](https://tokenmix.ai) — one API key for GPT-5, Claude, Gemini, DeepSeek and 155+ LLMs.

## Install

### Maven

```xml
<dependency>
    <groupId>io.github.tokenmixai</groupId>
    <artifactId>tokenmix-client</artifactId>
    <version>0.1.0</version>
</dependency>
```

### Gradle (Kotlin DSL)

```kotlin
implementation("io.github.tokenmixai:tokenmix-client:0.1.0")
```

### Gradle (Groovy)

```groovy
implementation 'io.github.tokenmixai:tokenmix-client:0.1.0'
```

## Usage

```java
import io.github.tokenmixai.TokenMix;
import java.util.List;

TokenMix client = new TokenMix(System.getenv("TOKENMIX_API_KEY"));

String reply = client.chat("gpt-5", List.of(
    new TokenMix.Message("user", "Hello!")
));
System.out.println(reply);

List<String> models = client.listModels();
System.out.println(models.size() + " models available");
```

## Get an API key

Free $1 credit at [tokenmix.ai](https://tokenmix.ai), no credit card required.

## Requirements

- Java 11+

## Other Languages

- **Python**: `pip install tokenmix-tg-bot`
- **Node.js**: `npm install -g tokenmix-tg-bot`
- **Rust**: `cargo install tokenmix-cli`
- **Ruby**: `gem install tokenmix`
- **Go**: `go get github.com/TokenMixAi/tg-ai-bot/go`
- **.NET**: `dotnet add package TokenMix.AI`
- **PHP**: `composer require tokenmixai/tokenmix-php`
- **Docker**: `docker pull tokenmixai/tg-ai-bot`

## Links

- Get API key: [tokenmix.ai](https://tokenmix.ai)
- Docs: [tokenmix.ai/docs](https://tokenmix.ai/docs)
- GitHub: [TokenMixAi/tg-ai-bot](https://github.com/TokenMixAi/tg-ai-bot)

## License

MIT
