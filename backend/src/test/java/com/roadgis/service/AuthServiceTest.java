package com.roadgis.service;

import com.roadgis.dto.request.LoginRequest;
import com.roadgis.dto.response.TokenResponse;
import com.roadgis.entity.User;
import com.roadgis.exception.BusinessException;
import com.roadgis.repository.UserRepository;
import com.roadgis.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.BDDMockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock UserRepository userRepository;
    @Mock PasswordEncoder passwordEncoder;
    @Mock JwtTokenProvider tokenProvider;
    @InjectMocks AuthService authService;

    private User mockUser;

    @BeforeEach
    void setUp() {
        mockUser = User.builder()
                .username("admin")
                .password("$2a$10$encodedPassword")
                .role("ADMIN")
                .build();
    }

    @Test
    @DisplayName("정상 로그인 시 토큰 반환")
    void login_success() {
        given(userRepository.findByUsername("admin")).willReturn(Optional.of(mockUser));
        given(passwordEncoder.matches("admin1234", mockUser.getPassword())).willReturn(true);
        given(tokenProvider.createToken("admin", "ADMIN")).willReturn("jwt-token");
        given(tokenProvider.getExpiration()).willReturn(86400000L);

        LoginRequest req = createLoginRequest("admin", "admin1234");
        TokenResponse result = authService.login(req);

        assertThat(result.getAccessToken()).isEqualTo("jwt-token");
        assertThat(result.getTokenType()).isEqualTo("Bearer");
    }

    @Test
    @DisplayName("존재하지 않는 사용자 로그인 시 UNAUTHORIZED")
    void login_userNotFound() {
        given(userRepository.findByUsername("unknown")).willReturn(Optional.empty());

        LoginRequest req = createLoginRequest("unknown", "password");

        assertThatThrownBy(() -> authService.login(req))
                .isInstanceOf(BusinessException.class)
                .satisfies(ex -> assertThat(((BusinessException) ex).getStatus()).isEqualTo(HttpStatus.UNAUTHORIZED));
    }

    @Test
    @DisplayName("비밀번호 불일치 시 UNAUTHORIZED")
    void login_wrongPassword() {
        given(userRepository.findByUsername("admin")).willReturn(Optional.of(mockUser));
        given(passwordEncoder.matches("wrongpass", mockUser.getPassword())).willReturn(false);

        LoginRequest req = createLoginRequest("admin", "wrongpass");

        assertThatThrownBy(() -> authService.login(req))
                .isInstanceOf(BusinessException.class)
                .satisfies(ex -> assertThat(((BusinessException) ex).getStatus()).isEqualTo(HttpStatus.UNAUTHORIZED));
    }

    private LoginRequest createLoginRequest(String username, String password) {
        try {
            LoginRequest req = new LoginRequest();
            var usernameField = LoginRequest.class.getDeclaredField("username");
            var passwordField = LoginRequest.class.getDeclaredField("password");
            usernameField.setAccessible(true);
            passwordField.setAccessible(true);
            usernameField.set(req, username);
            passwordField.set(req, password);
            return req;
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
