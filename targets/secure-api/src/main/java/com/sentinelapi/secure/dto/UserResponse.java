package com.sentinelapi.secure.dto;

public record UserResponse(
        Long id,
        String username,
        String fullName
) {
}
