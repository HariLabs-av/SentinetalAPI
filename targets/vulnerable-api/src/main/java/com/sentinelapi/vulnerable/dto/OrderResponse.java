package com.sentinelapi.vulnerable.dto;

import java.math.BigDecimal;

public record OrderResponse(
        Long id,
        Long ownerUserId,
        String ownerUsername,
        BigDecimal amount,
        String item
) {
}
