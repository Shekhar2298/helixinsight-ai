package com.helixinsight.orchestrator.controller;

import java.util.Map;
import com.helixinsight.orchestrator.service.BioApiClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class AnalysisController {
    private final BioApiClient bioApiClient;

    public AnalysisController(BioApiClient bioApiClient) {
        this.bioApiClient = bioApiClient;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of("status", "ok", "service", "orchestrator", "bioApi", bioApiClient.health());
    }

    @PostMapping("/biomarkers/train")
    public ResponseEntity<Map<?, ?>> train(@RequestBody Map<String, Object> request) {
        return ResponseEntity.ok(bioApiClient.trainBiomarkers(request));
    }

    @PostMapping("/reports/generate")
    public ResponseEntity<Map<?, ?>> report(@RequestBody Map<String, Object> request) {
        return ResponseEntity.ok(bioApiClient.generateReport(request));
    }
}
