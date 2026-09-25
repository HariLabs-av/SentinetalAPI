package com.sentinelapi.vulnerable.service;

import com.sentinelapi.vulnerable.dto.LoginRequest;
import com.sentinelapi.vulnerable.dto.LoginResponse;
import com.sentinelapi.vulnerable.entity.User;
import com.sentinelapi.vulnerable.repository.UserRepository;
import com.sentinelapi.vulnerable.security.JwtService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.username())
                .orElseThrow(() -> new IllegalArgumentException("Invalid username or password"));

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid username or password");
        }

        String token = jwtService.generateToken(user.getUsername(), user.getId());
        return new LoginResponse(token, user.getUsername(), user.getId());
    }
}
