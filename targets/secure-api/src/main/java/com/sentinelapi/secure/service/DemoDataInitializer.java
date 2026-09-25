package com.sentinelapi.secure.service;

import com.sentinelapi.secure.entity.Order;
import com.sentinelapi.secure.entity.User;
import com.sentinelapi.secure.repository.OrderRepository;
import com.sentinelapi.secure.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
public class DemoDataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final OrderRepository orderRepository;
    private final PasswordEncoder passwordEncoder;

    public DemoDataInitializer(UserRepository userRepository,
                               OrderRepository orderRepository,
                               PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        if (userRepository.count() > 0) {
            return;
        }

        User alice = new User("alice", passwordEncoder.encode("alice123"), "Alice Sharma");
        alice.setId(1L);
        alice = userRepository.save(alice);

        User bob = new User("bob", passwordEncoder.encode("bob123"), "Bob Verma");
        bob.setId(2L);
        bob = userRepository.save(bob);

        Order aliceOrder = new Order(alice, new BigDecimal("500.00"), "Laptop Stand");
        aliceOrder.setId(101L);
        orderRepository.save(aliceOrder);

        Order bobOrder = new Order(bob, new BigDecimal("900.00"), "Mechanical Keyboard");
        bobOrder.setId(102L);
        orderRepository.save(bobOrder);
    }
}
