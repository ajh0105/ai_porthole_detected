package com.roadgis.service;

import com.roadgis.dto.request.LoginRequest;
import com.roadgis.dto.response.TokenResponse;
import com.roadgis.entity.User;
import com.roadgis.exception.BusinessException;
import com.roadgis.repository.UserRepository;
import com.roadgis.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    public TokenResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> BusinessException.unauthorized("아이디 또는 비밀번호가 올바르지 않습니다."));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw BusinessException.unauthorized("아이디 또는 비밀번호가 올바르지 않습니다.");
        }

        String token = tokenProvider.createToken(user.getUsername(), user.getRole());
        return new TokenResponse(token, "Bearer", tokenProvider.getExpiration() / 1000);
    }
}
