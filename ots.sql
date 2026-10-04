-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 13, 2026 at 02:17 PM
-- Server version: 8.4.7
-- PHP Version: 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ots`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
CREATE TABLE IF NOT EXISTS `admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
CREATE TABLE IF NOT EXISTS `bookings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `menu_id` int NOT NULL,
  `booking_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'Pending',
  `quantity` int DEFAULT '1',
  `assigned_to` int DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `menu_id` (`menu_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `contact_messages`
--

DROP TABLE IF EXISTS `contact_messages`;
CREATE TABLE IF NOT EXISTS `contact_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` text COLLATE utf8mb4_unicode_ci,
  `date_posted` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
CREATE TABLE IF NOT EXISTS `menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `price` float NOT NULL,
  `image` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `menu`
--

INSERT INTO `menu` (`id`, `name`, `description`, `price`, `image`, `created_at`) VALUES
(1, 'Aloo Paratha', 'Whole wheat paratha stuffed with spiced mashed potatoes, served with yogurt and pickle.', 90, 'Aloo_paratha.jpg', '2026-04-04 16:21:10'),
(2, 'Baingan Bhartha', 'Roasted eggplant mashed with spices, tomatoes, onions and served with roti.', 100, 'baingan bhartha.jpg', '2026-04-04 16:21:10'),
(3, 'Besan Chilla', 'Savory gram flour pancakes with spices and chopped vegetables.', 70, 'besan_chilla.jpg', '2026-04-04 16:21:10'),
(4, 'Bread Butter', 'Soft buttered bread slices, lightly toasted.', 50, 'bread_butter.jpg', '2026-04-04 16:21:10'),
(5, 'Cheese Corn Sandwich', 'Whole wheat sandwich stuffed with melted cheese and sweet corn.', 90, 'cheese corn sandwich.jpg', '2026-04-04 16:21:10'),
(6, 'Cheese Corn', 'Sweet corn cooked with mild spices and topped with melted cheese.', 80, 'cheese_corn.jpg', '2026-04-04 16:21:10'),
(7, 'Chhole Bhature', 'Spicy chickpeas curry served with fluffy deep-fried bread.', 110, 'chhole_bhature.jpg', '2026-04-04 16:21:10'),
(8, 'Cutlet', 'Crispy vegetarian cutlet made with mashed vegetables and spices.', 60, 'cutlet.jpg', '2026-04-04 16:21:10'),
(9, 'Dal Rice', 'Steamed rice served with simple yellow dal tempered with spices.', 70, 'Dal_rice.jpg', '2026-04-04 16:21:10'),
(10, 'Dal Makhni', 'Creamy black lentil dal cooked with butter and spices, served with roti.', 120, 'Dal-Makhni.jpg', '2026-04-04 16:21:10'),
(11, 'Dhokla', 'Soft and spongy steamed gram flour snack, served with chutney.', 60, 'Dhokla.jpg', '2026-04-04 16:21:10'),
(12, 'Dosa', 'Crispy rice and lentil crepe served with sambar and coconut chutney.', 80, 'Dosa.jpg', '2026-04-04 16:21:10'),
(13, 'Garlic Naan & Shahi Veg.', 'Soft garlic naan served with rich and creamy mixed vegetable curry.', 150, 'Garlic naan & shahi veg.jpg', '2026-04-04 16:21:10'),
(14, 'Handavo', 'Savory Gujarati baked lentil cake with mild spices.', 70, 'Handavo.jpg', '2026-04-04 16:21:10'),
(15, 'Idli Sambhar', 'Steamed rice cakes served with spicy lentil sambar and coconut chutney.', 75, 'idli sambhar.jpg', '2026-04-04 16:21:10'),
(16, 'Jeera Dal', 'Yellow lentils tempered with cumin seeds, served with steamed rice.', 80, 'jeera dal.jpg', '2026-04-04 16:21:10'),
(17, 'Kadhi Khichdi', 'Soft khichdi served with tangy yogurt based kadhi.', 90, 'Kadhi-Khichdi.jpg', '2026-04-04 16:21:10'),
(18, 'Kaju Curry', 'Cashew nut curry cooked in creamy tomato and onion gravy.', 140, 'kaju curry.jpg', '2026-04-04 16:21:10'),
(19, 'Malai Kofta', 'Fried vegetable and paneer balls in creamy tomato gravy.', 130, 'malai cofta.jpg', '2026-04-04 16:21:10'),
(20, 'Manchurian Fried Rice', 'Vegetable fried rice tossed with Indo-Chinese Manchurian sauce.', 120, 'manchurian fried rice.jpg', '2026-04-04 16:21:10'),
(21, 'Matar Paneer', 'Soft paneer cubes cooked with green peas in tomato-based gravy.', 130, 'matar paneer.jpg', '2026-04-04 16:21:10'),
(22, 'Mix Veg Curry', 'Seasonal vegetables cooked with mild Indian spices.', 110, 'mix-veg-curry.jpg', '2026-04-04 16:21:10'),
(23, 'Moog Chilla', 'Savory pancake made with moong dal and spices.', 70, 'moog chilla.jpg', '2026-04-04 16:21:10'),
(24, 'Palak Paneer', 'Spinach curry with soft paneer cubes and Indian spices.', 130, 'palak paneer.jpg', '2026-04-04 16:21:10'),
(25, 'Paneer Butter Masala', 'Soft paneer cubes cooked in creamy tomato butter gravy.', 140, 'Paneer_butter_masala.jpg', '2026-04-04 16:21:10'),
(26, 'Pav Bhaji', 'Mashed spicy vegetable curry served with buttered buns.', 100, 'pav bhaji.jpg', '2026-04-04 16:21:10'),
(27, 'Plain Paratha', 'Soft whole wheat paratha served with pickle or yogurt.', 60, 'plain paratha.jpg', '2026-04-04 16:21:10'),
(28, 'Poha', 'Flattened rice sautéed with onions, green chilies, peanuts, and curry leaves.', 60, 'poha.jpg', '2026-04-04 16:21:10'),
(29, 'Rajma Chawal', 'Red kidney beans curry served with steamed rice.', 100, 'Rajma_chawal.jpg', '2026-04-04 16:21:10'),
(30, 'Sandwich', 'Whole wheat sandwich stuffed with fresh vegetables.', 70, 'sandwich.jpg', '2026-04-04 16:21:10'),
(31, 'Sev Usal', 'Spicy curry made from white peas topped with crunchy sev.', 90, 'sev usal.jpg', '2026-04-04 16:21:10'),
(32, 'Stuffed Paratha', 'Paratha stuffed with spiced vegetables or paneer, served with yogurt.', 80, 'stuffed paratha.jpg', '2026-04-04 16:21:10'),
(33, 'Sweet Corn Soup', 'Warm soup made from sweet corn, mild spices, and cream.', 70, 'sweet corn soup.jpg', '2026-04-04 16:21:10'),
(34, 'Tandoori Roti Sabji', 'Tandoori roti served with seasonal vegetable curry.', 100, 'Tandoori roti sabji.jpg', '2026-04-04 16:21:10'),
(35, 'Thepla', 'Gujarati spiced flatbread made with fenugreek leaves, served with pickle.', 60, 'Thepla.jpg', '2026-04-04 16:21:10'),
(36, 'Tomato Rice', 'Fragrant rice cooked with tomatoes and Indian spices.', 70, 'tomato rice.jpg', '2026-04-04 16:21:10'),
(37, 'Tomato Soup', 'Smooth tomato soup with light seasoning, served hot.', 60, 'Tomato soup.jpg', '2026-04-04 16:21:10'),
(38, 'Undhiyu', 'Mixed vegetables and beans slow-cooked with Indian spices.', 120, 'undhiyu.jpg', '2026-04-04 16:21:10'),
(39, 'Upma', 'Savory semolina dish cooked with vegetables and spices.', 60, 'Upma.jpg', '2026-04-04 16:21:10'),
(40, 'Veg Kolhapuri', 'Spicy Kolhapuri-style mixed vegetable curry.', 130, 'veg kolhapuri.jpg', '2026-04-04 16:21:10'),
(41, 'Veg Pulav', 'Basmati rice cooked with vegetables and aromatic spices.', 110, 'veg pulav.jpg', '2026-04-04 16:21:10'),
(42, 'Veg Thali', 'Assorted vegetarian dishes served together with roti, rice, dal, and sweets.', 180, 'Veg_thali.jpg', '2026-04-04 16:21:10');

-- --------------------------------------------------------

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
CREATE TABLE IF NOT EXISTS `ratings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `menu_id` int DEFAULT NULL,
  `rate` int NOT NULL,
  `comment` text COLLATE utf8mb4_unicode_ci,
  `rating_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

DROP TABLE IF EXISTS `staff`;
CREATE TABLE IF NOT EXISTS `staff` (
  `s_id` int NOT NULL AUTO_INCREMENT,
  `s_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `s_email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `s_phone` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `s_role` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`s_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
