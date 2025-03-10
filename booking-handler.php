<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'vendor/autoload.php';

// Load SMTP credentials securely
$config = require 'config.php'; // Load credentials

$mail = new PHPMailer(true);

try {
    $mail->isSMTP();
    $mail->Host = 'smtp.gmail.com';
    $mail->SMTPAuth = true;
    $mail->Username = $config['SMTP_USER']; // Securely loaded
    $mail->Password = $config['SMTP_PASS']; // Securely loaded
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
?>
