# Frontend Services - DDD Implementation

## AddressService

The `AddressService` follows Domain-Driven Design (DDD) principles by encapsulating address-related business logic and separating it from UI components.

### Purpose

This service abstracts the logic for managing user addresses, specifically:
- Getting the default address (with localStorage caching)
- Setting selected addresses
- Managing address cache

### Key Benefits

1. **Single Responsibility**: The service only handles address-related operations
2. **Reusability**: Can be used across multiple components without code duplication
3. **Maintainability**: Address logic is centralized and easier to modify
4. **Testability**: Business logic is separated from UI, making it easier to test
5. **DDD Compliance**: Follows domain boundaries and encapsulates business rules

### Usage

```javascript
import AddressService from '../services/addressService.js'

// Get default address (with caching)
const address = await AddressService.getDefaultAddress(userId)

// Set selected address
AddressService.setSelectedAddress(address)

// Clear selected address
AddressService.clearSelectedAddress()

// Get cached address
const cachedAddress = AddressService.getSelectedAddress()
```

### Implementation Details

The service implements a caching strategy:
1. **Priority**: localStorage → Backend API
2. **Caching**: Automatically caches default addresses
3. **Error Handling**: Graceful fallbacks and error logging
4. **Consistency**: Same logic across all components

### Components Updated

- `checkout.vue`: Uses `AddressService.getDefaultAddress()`
- `product-detail.vue`: Uses `AddressService.getDefaultAddress()` and `AddressService.setSelectedAddress()`
- `address-list.vue`: Uses `AddressService.setSelectedAddress()`

### Future Enhancements

- Add address validation logic
- Implement address geocoding
- Add address format standardization
- Support multiple address types (home, work, etc.) 