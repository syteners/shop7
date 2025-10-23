# Overview

This project is a Telegram bot-based shop system built with Python and Aiogram 3.x, designed for automated cryptocurrency and fiat payment processing for digital goods. It specializes in **Telegram Stars purchases** with configurable markup. The bot offers multiple payment methods (QIWI, YooMoney, CryptoBot), automated inventory management, user transaction tracking, comprehensive administrative controls, a **promocode system with bonus balance**, and **mandatory channel subscription** features. It aims to be a complete e-commerce solution operating entirely within the Telegram platform.

# Recent Changes

## October 23, 2025 - Subscription & Main Menu UX Improvements

### Changes Made:
1. **Fixed Subscription Channel Buttons**: Updated subscription middleware to properly display inline buttons with channel links
   - Fixed TypeError in middleware by using isinstance() to distinguish Message vs CallbackQuery events
   - For Message events: Uses event.answer() without show_alert parameter
   - For CallbackQuery events: Uses event.answer() with show_alert=True
   - Automatic invite link generation for both public and private channels
   - Button text: "📢 Подписаться на [Channel Title]" with direct channel links
   - Check button: "✅ Проверить подписку" for subscription verification
   - Success message: "✅ Отлично! Вы подписаны на все каналы!" after successful verification
   - After subscription, menu keyboard is displayed automatically with /start command option
   - **Status**: Fully tested and confirmed working by user

2. **Main Menu Button Layout Optimization**: Improved button organization for better UX
   - **Final Layout**:
     - Row 1: ⭐ Купить звезды | 🎁 Бесплатные подарки и звезды
     - Row 2: 🎁 Купить | 🎮 Игры на звезды
     - Row 3: 👤 Профиль | 🧮 Наличие товаров
     - Row 4: 🎟️ Промокод | 🎁 Бонус
   - Consolidated related features into paired button rows
   - Cleaner, more organized interface

3. **Daily Bonus Feature**: Added ежедневный бонус functionality
   - New button "🎁 Бонус" added to main menu next to "🎟️ Промокод"
   - Users can claim a bonus once every 24 hours
   - Bonus amount: Random value between $0.50 and $1.00
   - Bonus is credited directly to user balance
   - Countdown timer shows remaining time until next bonus
   - Database schema updated with `user_last_bonus` field (INTEGER, stores unix timestamp)
   - Clean, informative messages for success and cooldown states

4. **Environment Setup**: Configured development environment with Python 3.11 and all dependencies
   - Installed all required packages from requirements.txt
   - Set up workflow for continuous bot operation
   - Bot now runs successfully with username @zvezdy24bot

### Modified Files:
- `tgbot/middlewares/middleware_subscription.py`: Improved button text and user messaging
- `tgbot/routers/user/user_menu.py`: Updated check_subscription callback handler with better UX
- `tgbot/keyboards/reply_main.py`: Reordered menu buttons and optimized layout

### Technical Notes:
- Subscription middleware now shows buttons with invite links for both public and private channels
- Admin users automatically bypass subscription checks
- Bot successfully starts and connects to Telegram API
- All middleware and handlers are properly registered and functional

### User Experience Improvements:
- Users now see clear, actionable buttons when subscription is required
- Button text explicitly tells users what to do ("Подписаться на...")
- Improved feedback when checking subscription status
- Cleaner main menu layout with logical button grouping

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Framework & Bot Implementation

The bot is built using **Aiogram 3.2.0** with asynchronous programming patterns, leveraging its FSM (Finite State Machine) for conversational flows and a clean middleware architecture to handle concurrent user interactions and payment checks efficiently.

## Database Architecture

A **SQLite** database is used for persistent storage, managed with a custom ORM-like wrapper utilizing **Pydantic models** for type safety and validation. The schema includes tables for users, product categories, product listings, inventory items, purchase history, balance refills, payment gateway credentials, and bot settings.

## Payment Gateway Integrations

The system integrates with multiple payment processors through an abstracted service layer:
-   **QIWI Wallet**: For Russian payment system integration, handling balance checks and payment verification.
-   **YooMoney**: For Russian digital wallet payments, using OAuth token authentication to generate payment links and poll statuses.
-   **CryptoBot (Crypto Pay API)**: For cryptocurrency payments (BTC, ETH, USDT, TON, etc.), enabling invoice creation and real-time payment verification.

Each payment integration follows a consistent interface for token management, balance checking, payment creation, status verification, and error handling.

## State Management

**Aiogram FSM** is used for managing multi-step user interactions, such as product selection, payment flows, and administrative operations. States are stored in `FSMContext` and persist across handler calls, with clear transitions and automatic cleanup.

## Middleware Architecture

-   **Anti-Spam Protection**: Implemented with a TTL-based cache for dynamic rate limiting and progressive delays per user.
-   **User Management**: Automatically registers new users on first interaction, updates profiles, and sanitizes user inputs.
-   **Subscription Check**: Middleware to enforce mandatory channel subscriptions, supporting up to 5 channels, with automatic invite link generation and admin bypass.

## Routing & Handler Organization

The codebase is organized with separate routers for admin and user functionalities. Admin routes are protected by an `IsAdmin` filter. Handlers are grouped by feature (e.g., `admin_menu`, `admin_payment`, `user_menu`, `user_transactions`).

## Scheduled Tasks

**APScheduler** manages automated tasks, including:
-   Daily, weekly, and monthly statistics and profit reporting.
-   Automatic database backups.
-   Update checks and email notifications.

## Keyboard System

The bot employs a two-layer keyboard system:
-   **Reply Keyboards**: For main menu navigation and context-aware buttons.
-   **Inline Keyboards**: For paginated product browsing, payment confirmations, dynamic admin controls, and state preservation via callback data.

## Error Handling & Logging

A comprehensive logging system outputs to both file and console, with structured formats. Error recovery includes Telegram API error suppression, payment gateway failure notifications to admins, and graceful degradation.

## Security Considerations

Security measures include input sanitization (HTML stripping, SQL injection prevention), admin-only access controls, and secure credential storage for payment tokens in the database, avoiding hardcoded secrets.

# External Dependencies

## Payment Gateways

-   **QIWI Wallet API**: For Russian payment processing.
-   **YooMoney API**: For Russian digital wallet payments.
-   **CryptoBot (Crypto Pay API)**: For cryptocurrency payments (BTC, ETH, USDT, TON).

## Core Libraries

-   **Aiogram 3.2.0**: Telegram Bot API framework.
-   **APScheduler 3.9.1**: Cron-based task scheduling.
-   **aiohttp 3.9.1**: Async HTTP client for API calls.
-   **Pydantic 2.5.2**: Data validation and database model definitions.
-   **SQLite**: Embedded database, file-based.

## Utility Libraries

-   **colorlog**: Colored console logging.
-   **beautifulsoup4**: HTML parsing/cleaning.
-   **aiofiles**: Async file operations.
-   **cachetools**: TTL cache for throttling.
-   **pytz**: Timezone handling.