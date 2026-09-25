package com.sentinelapi.secure.dto;

import java.math.BigDecimal;

public record OrderResponse(
        Long id,
        Long ownerUserId,
        String ownerUsername,
        BigDecimal amount,
        String item
) {
}
