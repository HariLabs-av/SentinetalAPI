package com.sentinelapi.vulnerable.repository;

import com.sentinelapi.vulnerable.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
}
