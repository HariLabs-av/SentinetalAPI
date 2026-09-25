package com.sentinelapi.secure.dto;

public record LoginResponse(String token, String username, Long userId) {
}
