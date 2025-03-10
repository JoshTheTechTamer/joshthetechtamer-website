<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'vendor/autoload.php'; // Load PHPMailer via Composer

// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST['name'] ?? '';
    $email = $_POST['email'] ?? '';
    $phone = $_POST['phone'] ?? '';
    $topic = $_POST['topic'] ?? '';
    $date = $_POST['date'] ?? '';
    $time = $_POST['time'] ?? '';

    // Validate required fields
    if (empty($name) || empty($email) || empty($phone) || empty($topic) || empty($date) || empty($time)) {
        echo json_encode(["status" => "error", "message" => "All fields are required."]);
        exit();
    }

    $mail = new PHPMailer(true);

    try {
        // SMTP Settings
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com'; // Gmail SMTP server
        $mail->SMTPAuth = true;
        $mail->Username = 'joshthetechtamer@gmail.com'; // 🔹 REPLACE with your Gmail
        $mail->Password = 'yrou wypv bbcw hfdz';  // 🔹 REPLACE with your App Password
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; 
        $mail->Port = 587;

        // Email Details
        $mail->setFrom('joshthetechtamer@gmail.com', 'The Tech Tamer'); // Sender
        $mail->addAddress('joshthetechtamer@gmail.com'); // 🔹 Your email (where bookings are sent)
        $mail->addReplyTo($email, $name); // Allow replies to user's email

        $mail->Subject = "New Booking from $name";
        $mail->Body = "
        A new booking has been received:
        
        Name: $name
        Email: $email
        Phone: $phone
        Consultation Topic: $topic
        Date: $date
        Time: $time

        Please follow up as needed.";

        $mail->send();
        echo json_encode(["status" => "success", "message" => "Booking request sent successfully."]);
    } catch (Exception $e) {
        echo json_encode(["status" => "error", "message" => "Mailer Error: {$mail->ErrorInfo}"]);
    }
} else {
    echo json_encode(["status" => "error", "message" => "Invalid request."]);
}
?>
