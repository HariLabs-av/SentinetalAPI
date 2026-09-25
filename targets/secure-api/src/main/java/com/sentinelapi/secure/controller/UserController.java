package com.sentinelapi.secure.controller;

import com.sentinelapi.secure.dto.UserResponse;
import com.sentinelapi.secure.entity.User;
import com.sentinelapi.secure.repository.UserRepository;
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
@RequestMapping("/api/users")
@Tag(name = "Users")
@SecurityRequirement(name = "bearerAuth")
public class UserController {

    private final UserRepository userRepository;

    public UserController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @GetMapping("/{id}")
    @Operation(
            summary = "Get the authenticated user by ID",
            description = "Secure version: object-level authorization is enforced. A user cannot read another user's profile."
    )
    public ResponseEntity<UserResponse> getUser(
            @PathVariable Long id,
            Authentication authentication
    ) {
        User user = userRepository.findById(id).orElse(null);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        if (authentication == null || !authentication.getName().equals(user.getUsername())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }

        return ResponseEntity.ok(toResponse(user));
    }

    @GetMapping
    @Operation(
            summary = "Get the authenticated user's profile",
            description = "Secure version: returns only the current user's safe public profile fields. Password hashes and other authentication secrets are never serialized."
    )
    public List<UserResponse> getUsers(Authentication authentication) {
        return userRepository.findByUsername(authentication.getName())
                .map(user -> List.of(toResponse(user)))
                .orElseGet(List::of);
    }

    private UserResponse toResponse(User user) {
        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getFullName()
        );
    }
}
