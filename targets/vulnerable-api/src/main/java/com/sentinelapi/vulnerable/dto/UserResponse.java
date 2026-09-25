package com.sentinelapi.vulnerable.dto;

public record UserResponse(
        Long id,
        String username,
        String fullName,
        String passwordHash
) {
}
