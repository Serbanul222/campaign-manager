/**
 * JWT utility functions for token handling
 */

/**
 * Decode JWT token (without verification - client-side only)
 * Note: This doesn't verify the token signature, just decodes the payload
 */
export const decodeJWT = (token) => {
  try {
    // JWT has three parts separated by dots
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }

    // Decode the payload (second part)
    const payload = parts[1];
    
    // Add padding if needed (JWT base64 might not have padding)
    const paddedPayload = payload + '==='.slice((payload.length + 3) % 4);
    
    // Decode base64
    const decodedPayload = atob(paddedPayload);
    
    // Parse JSON
    return JSON.parse(decodedPayload);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
};

/**
 * Check if JWT token is expired
 */
export const isTokenExpired = (token) => {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) {
    return true; // Consider invalid tokens as expired
  }

  // Convert exp from seconds to milliseconds and compare with current time
  const expirationTime = decoded.exp * 1000;
  return Date.now() >= expirationTime;
};

/**
 * Get user info from JWT token
 */
export const getUserFromToken = (token) => {
  const decoded = decodeJWT(token);
  if (!decoded) {
    return null;
  }

  // Extract user information from token payload
  // The 'sub' field typically contains the user ID
  return {
    id: decoded.sub,
    iat: decoded.iat,
    exp: decoded.exp,
    jti: decoded.jti
  };
};