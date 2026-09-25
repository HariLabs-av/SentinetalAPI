package com.sentinelapi.vulnerable.controller;

import com.sentinelapi.vulnerable.dto.OrderResponse;
import com.sentinelapi.vulnerable.entity.Order;
import com.sentinelapi.vulnerable.repository.OrderRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/orders")
@Tag(name = "Orders")
@SecurityRequirement(name = "bearerAuth")
public class OrderController {

    private final OrderRepository orderRepository;

    public OrderController(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @GetMapping("/{id}")
    @Operation(
            summary = "Get an order by ID",
            description = "INTENTIONALLY VULNERABLE: authentication is required, but the API does not verify that the authenticated user owns the requested order. This endpoint exists so SentinelAPI can detect BOLA."
    )
    public ResponseEntity<OrderResponse> getOrder(@PathVariable Long id, Authentication authentication) {
        Order order = orderRepository.findById(id).orElse(null);
        if (order == null) {
            return ResponseEntity.notFound().build();
        }

        // INTENTIONALLY VULNERABLE:
        // We authenticate the caller, but we DO NOT check whether
        // authentication.getName() owns this order.
        return ResponseEntity.ok(toResponse(order, authentication));
    }

    @GetMapping
    @Operation(
            summary = "List all orders",
            description = "INTENTIONALLY OVER-PERMISSIVE DEMO ENDPOINT: returns every demo order to any authenticated user."
    )
    public List<OrderResponse> getAllOrders(Authentication authentication) {
        return orderRepository.findAll().stream()
                .map(order -> toResponse(order, authentication))
                .toList();
    }

    private OrderResponse toResponse(Order order, Authentication authentication) {
        return new OrderResponse(
                order.getId(),
                order.getUser().getId(),
                order.getUser().getUsername(),
                order.getAmount(),
                order.getItem()
        );
    }
}
