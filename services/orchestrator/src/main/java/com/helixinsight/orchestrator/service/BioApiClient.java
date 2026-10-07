package com.helixinsight.orchestrator.service;

import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class BioApiClient {
    private final RestClient client;

    public BioApiClient(@Value("${bio.api.url}") String baseUrl) {
        this.client = RestClient.builder().baseUrl(baseUrl).build();
    }

    public Map<?, ?> health() {
        return client.get().uri("/health").retrieve().body(Map.class);
    }

    public Map<?, ?> trainBiomarkers(Map<String, Object> request) {
        return client.post().uri("/v1/biomarkers/train")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve().body(Map.class);
    }

    public Map<?, ?> generateReport(Map<String, Object> request) {
        return client.post().uri("/v1/reports/generate")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve().body(Map.class);
    }
}
