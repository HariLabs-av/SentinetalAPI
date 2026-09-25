package com.sentinelapi.secure.repository;

import com.sentinelapi.secure.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface OrderRepository extends JpaRepository<Order, Long> {

    List<Order> findAllByUser_UsernameOrderByIdAsc(String username);
}
