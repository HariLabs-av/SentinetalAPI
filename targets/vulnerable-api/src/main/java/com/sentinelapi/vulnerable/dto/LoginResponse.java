package com.sentinelapi.vulnerable.dto;

public record LoginResponse(String token, String username, Long userId) {
}
