package com.sentinelapi.vulnerable;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class VulnerableApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(VulnerableApiApplication.class, args);
    }
}
