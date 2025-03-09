<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST['name'] ?? '';
    $email = $_POST['email'] ?? '';
    $phone = $_POST['phone'] ?? '';
    $topic = $_POST['topic'] ?? '';
    $date = $_POST['date'] ?? '';
    $time = $_POST['time'] ?? '';

    if (empty($name) || empty($email) || empty($phone) || empty($topic) || empty($date) || empty($time)) {
        echo json_encode(["status" => "error", "message" => "All fields are required."]);
        exit();
    }

    $to = "joshthetechtamer@gmail.com"; // Your email
    $subject = "New Booking Request from $name";
    $message = "
    A new booking has been received:
    
    Name: $name
    Email: $email
    Phone: $phone
    Consultation Topic: $topic
    Date: $date
    Time: $time

    Please follow up as needed.";

    $headers = "From: no-reply@yourdomain.com\r\n";
    $headers .= "Reply-To: $email\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

    if (mail($to, $subject, $message, $headers)) {
        echo json_encode(["status" => "success", "message" => "Booking request sent successfully."]);
    } else {
        echo json_encode(["status" => "error", "message" => "Failed to send email."]);
    }
} else {
    echo json_encode(["status" => "error", "message" => "Invalid request."]);
}
?>
