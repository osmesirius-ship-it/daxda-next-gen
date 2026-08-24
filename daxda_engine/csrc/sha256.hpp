#ifndef SHA256_HPP
#define SHA256_HPP

#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <cstring>

class SHA256 {
public:
    SHA256() { reset(); }

    void reset() {
        m_l = 0;
        m_h[0] = 0x6a09e667;
        m_h[1] = 0xbb67ae85;
        m_h[2] = 0x3c6ef372;
        m_h[3] = 0xa54ff53a;
        m_h[4] = 0x510e527f;
        m_h[5] = 0x9b05688c;
        m_h[6] = 0x1f83d9ab;
        m_h[7] = 0x5be0cd19;
    }

    void update(const uint8_t *data, size_t length) {
        for (size_t i = 0; i < length; ++i) {
            m_data[m_l % 64] = data[i];
            m_l++;
            if (m_l % 64 == 0) {
                transform();
            }
        }
    }

    void update(const std::string &data) {
        update(reinterpret_cast<const uint8_t*>(data.c_str()), data.length());
    }

    std::string final() {
        uint8_t i = m_l % 64;
        m_data[i++] = 0x80;

        if (i > 56) {
            while (i < 64) {
                m_data[i++] = 0x00;
            }
            transform();
            memset(m_data, 0, 56);
        } else {
            while (i < 56) {
                m_data[i++] = 0x00;
            }
        }

        uint64_t total_bits = m_l * 8;
        for (int j = 7; j >= 0; --j) {
            m_data[56 + (7 - j)] = (total_bits >> (j * 8)) & 0xFF;
        }

        transform();

        std::ostringstream ss;
        for (int j = 0; j < 8; ++j) {
            ss << std::hex << std::setw(8) << std::setfill('0') << m_h[j];
        }
        return ss.str();
    }

    static std::string hash(const std::string &data) {
        SHA256 sha;
        sha.update(data);
        return sha.final();
    }

private:
    uint32_t m_h[8];
    uint8_t m_data[64];
    uint64_t m_l;

    static inline uint32_t rotr(uint32_t x, uint32_t n) {
        return (x >> n) | (x << (32 - n));
    }
    static inline uint32_t choose(uint32_t e, uint32_t f, uint32_t g) {
        return (e & f) ^ (~e & g);
    }
    static inline uint32_t majority(uint32_t a, uint32_t b, uint32_t c) {
        return (a & b) ^ (a & c) ^ (b & c);
    }
    static inline uint32_t sig0(uint32_t x) {
        return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
    }
    static inline uint32_t sig1(uint32_t x) {
        return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
    }
    static inline uint32_t sub0(uint32_t x) {
        return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
    }
    static inline uint32_t sub1(uint32_t x) {
        return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
    }

    void transform() {
        static const uint32_t K[64] = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef4a3f7, 0xc67178f2
        };

        uint32_t w[64];
        for (int i = 0; i < 16; ++i) {
            w[i] = (m_data[i * 4] << 24) | (m_data[i * 4 + 1] << 16) | (m_data[i * 4 + 2] << 8) | (m_data[i * 4 + 3]);
        }
        for (int i = 16; i < 64; ++i) {
            w[i] = sub1(w[i - 2]) + w[i - 7] + sub0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = m_h[0];
        uint32_t b = m_h[1];
        uint32_t c = m_h[2];
        uint32_t d = m_h[3];
        uint32_t e = m_h[4];
        uint32_t f = m_h[5];
        uint32_t g = m_h[6];
        uint32_t h = m_h[7];

        for (int i = 0; i < 64; ++i) {
            uint32_t t1 = h + sig1(e) + choose(e, f, g) + K[i] + w[i];
            uint32_t t2 = sig0(a) + majority(a, b, c);
            h = g;
            g = f;
            f = e;
            e = d + t1;
            d = c;
            c = b;
            b = a;
            a = t1 + t2;
        }

        m_h[0] += a;
        m_h[1] += b;
        m_h[2] += c;
        m_h[3] += d;
        m_h[4] += e;
        m_h[5] += f;
        m_h[6] += g;
        m_h[7] += h;
    }
};

#endif // SHA256_HPP
