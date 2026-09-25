package com.sentinelapi.secure.controller;

import com.sentinelapi.secure.dto.OrderResponse;
import com.sentinelapi.secure.entity.Order;
import com.sentinelapi.secure.repository.OrderRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpStatus;
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
            summary = "Get the authenticated user's order by ID",
            description = "Secure version: object-level authorization is enforced. A user cannot read another user's order."
    )
    public ResponseEntity<OrderResponse> getOrder(
            @PathVariable Long id,
            Authentication authentication
    ) {
        Order order = orderRepository.findById(id).orElse(null);

        if (order == null) {
            return ResponseEntity.notFound().build();
        }

        if (!ownsOrder(order, authentication)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }

        return ResponseEntity.ok(toResponse(order));
    }

    @GetMapping
    @Operation(
            summary = "List the authenticated user's orders",
            description = "Secure version: only orders owned by the authenticated user are returned."
    )
    public List<OrderResponse> getMyOrders(Authentication authentication) {
        return orderRepository.findAllByUser_UsernameOrderByIdAsc(authentication.getName())
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private boolean ownsOrder(Order order, Authentication authentication) {
        return authentication != null
                && authentication.getName().equals(order.getUser().getUsername());
    }

    private OrderResponse toResponse(Order order) {
        return new OrderResponse(
                order.getId(),
                order.getUser().getId(),
                order.getUser().getUsername(),
                order.getAmount(),
                order.getItem()
        );
    }
}
