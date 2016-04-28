var current_user_name = $("#current_user").text();
var user_chatting_with = null;

function scrollChatHistoryToBottom() {
    $("#chatHistory").animate({ scrollTop: $("#chatHistory")[0].scrollHeight}, 0);
}

function printMessage(message) {
    if (message.sender === current_user_name) {
        $('#chatHistory').append('<p><span class=\'fromMe\'>' +
            message.sender + ':</span>&nbsp&nbsp&nbsp&nbsp&nbsp' +
            message.message_content + '</p>');
    } else {
        $('#chatHistory').append('<p><span class=\'fromOtherPerson\'>' +
            message.sender + ':</span>&nbsp&nbsp&nbsp&nbsp&nbsp' +
            message.message_content + '</p>');
    }
    scrollChatHistoryToBottom();
}

function showChatHistory(messages) {
    $('#chatHistory').empty();
    for (i = 0 ; i < messages.length ; i++) {
        var message = messages[i];
        printMessage(message);
    }
}

function displayNewMessage(message) {
    if (message.sender === user_chatting_with || message.receiver === user_chatting_with) {
        printMessage(message);
    } else {
        $('a:contains(' + message.sender + ')').append('<sup class=\'newMessage\'>&nbsp;NEW MESSAGE</sup>');
    }
}

$(document).ready(function() {
    $('.users a').bind('click', function(e) {
        e.preventDefault();
        user_chatting_with = $(this).children().remove().end().text();
        $('.users a').removeAttr('class');

        $(this).attr('class','selectedUser');

        $('#otherUser').empty();
        $('#otherUser').append('<h2>' + user_chatting_with + '</h2>');

        $('#messageForm').children().removeAttr('disabled');

        $.ajax({
            type: "GET",
            url: "/chat-history/" + user_chatting_with,
            accepts: "application/json",
            success: function(data) {
                showChatHistory(data.messages);
            }
        });
    });

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('message', function(data) {
        displayNewMessage(data);
    });

    $('#messageForm').on('submit', function(e) {
        e.preventDefault();
        var message = $('input[name=message]').val();
        socket.emit('text', {sender: current_user_name, receiver: user_chatting_with, message_content: message})
    });
});
