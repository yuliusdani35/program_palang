-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 09, 2024 at 08:04 PM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 8.0.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `attendancedb`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `hours_in` time NOT NULL,
  `hours_out` time NOT NULL,
  `predict_time` int(11) NOT NULL DEFAULT 0,
  `path` varchar(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`id`, `name`, `date`, `hours_in`, `hours_out`, `predict_time`, `path`) VALUES
(1, 'ula', '2024-06-20', '14:27:33', '14:29:14', 0, ''),
(2, 'dani', '0000-00-00', '23:36:11', '00:00:00', 0, ''),
(3, 'dani', '2024-07-29', '23:52:48', '00:00:00', 0, ''),
(4, 'dani', '2024-07-30', '23:59:28', '00:19:37', 1733, ''),
(5, 'Unknown', '2024-07-30', '23:49:09', '00:00:00', 1812, ''),
(6, 'dani', '2024-07-31', '00:03:56', '00:09:31', 1392, ''),
(7, 'dani', '2024-08-03', '10:59:08', '09:40:51', 2044, 'G:\\Program palang\\output\\main2\\_internal/output/03082024_105908_dani.png'),
(8, 'dani', '2024-08-05', '14:01:04', '00:00:00', 2080, 'G:\\Program palang/output/05082024_140104_dani.png'),
(9, 'Unknown', '2024-08-05', '14:16:12', '00:00:00', 1468, 'G:\\Program palang/output/05082024_141612_Unknown.png'),
(10, 'angel', '2024-08-05', '14:25:37', '00:00:00', 1551, 'G:\\Program palang/output/05082024_142537_angel.png'),
(11, 'dani', '2024-08-06', '14:59:59', '00:00:00', 1927, 'G:\\Program palang/output/06082024_145959_dani.png'),
(12, 'angel', '2024-08-06', '18:40:03', '00:00:00', 1545, 'G:\\Program palang/output/06082024_184003_angel.png'),
(13, 'Unknown', '2024-08-06', '18:39:35', '00:00:00', 1514, 'G:\\Program palang/output/06082024_183935_Unknown.png'),
(14, 'lala', '2024-08-06', '15:09:37', '00:00:00', 1669, 'G:\\Program palang/output/06082024_150937_lala.png'),
(15, 'Alvin', '2024-08-06', '18:37:46', '00:00:00', 1512, 'G:\\Program palang/output/06082024_183746_Alvin.png'),
(16, 'dani', '2024-08-09', '14:34:20', '00:00:00', 1852, 'G:\\Program palang/output/09082024_143420_dani.png'),
(17, 'dani', '2024-08-10', '00:53:50', '00:00:00', 1634, 'G:\\Program palang/output/10082024_005350_dani.png');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
