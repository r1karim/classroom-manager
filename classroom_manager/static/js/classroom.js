selected_channel = null;
selected_classroom = null;
const clear_chatbox = () => {
	const chat_box = $('#channel_display .messagescontainer').first();
	chat_box.html('');
}
const set_chat_title = (server_title,channel_title) => {
	const chat_title = $('#channel_display .upper_part .title').first(); //getting the first h4 element inside of the channel_display element
	chat_title.html(`<b>${server_title}</b> ${channel_title}`);
	$(chat_title).find('i').remove();
}
const clear_submissions = () => {
	$('#submissions').html('');
}
const add_message = (message_data) => {
	const chat_box = $('#channel_display .messagescontainer').first();
	chat_box.append(`<div class="message bg-light"><span><b>${message_data.author.name}</b> ${message_data.date}</span><p>${message_data.content}</p></div>`);
	$(chat_box).scrollTop(10000);
}
const clear_notes = () => {
	const notes = $('#note-container');
	const notes_list = $ ('#note-list');
	notes.html('');
	notes_list.html('');
}
const add_note = (note_data, active) => {
	const note_list = $('#note-list');
	const note_container = $('#note-container');
	let id = note_data.note_title.replaceAll(' ', '') + note_data.note_id.toString(10);
	note_list.append(`<a class="list-group-item list-group-item-action ${active}" data-toggle="list" href="#${id}" role="tab" style='z-index:0;'>${note_data.note_title}</a>`);
	additional_text = '';
	if(note_data.note_img) {
		additional_text += `<img src="${note_data.note_img}" style='max-width:600px; max-height:600px;' />`;
	}
	note_container.append(`<div class="tab-pane ${active}" id="${id}" role="tabpanel">${additional_text}<p>${note_data.note_text}</p></div>`);
}
const add_assignment = (assignment_data, is_super) => {
	const assignment_list = $('#assignments-list');
	if (assignment_data.id) {
		if(is_super) {
			assignment_list.append(`<tr value=${assignment_data.id}><td>${assignment_data.text}</td><td>${assignment_data.duedate}</td><td><button class='show_submission_button' data-target='#submissions'>View submissions</button> </td> </tr>`);
		}
		else {
			if (assignment_data.submission_state) {
				assignment_list.append(`<tr value=${assignment_data.id}><td>${assignment_data.text}</td><td>${assignment_data.duedate}</td><td>Already submitted</td> </tr>`);
			}
			else {
				assignment_list.append(`<tr value=${assignment_data.id}><td>${assignment_data.text}</td><td>${assignment_data.duedate}</td><td><form id='homework_submission'><input type=file name=homework><button>submit</button></form></td></tr>`);

			}
		}	
	}
}
const clear_assignments = () => {
	const assignment_list = $('#assignments-list');
	assignment_list.html('');
}
const toggle_submissions_menu = () => {
	$('#testest').css('display', 'block');
}
$(document).ready(function() {
	$('body').click(function(e) {
		var target = $(e.target);
		if(!target.is('#new_conversation_form') && !target.is('#new_conversation_form input')) {
			is_visible = $('#new_conversation_form').css('display');
			if (is_visible != 'none') {
				$('#new_conversation_form').css('display', 'none');
				$('#newconversation').css('display', 'block');
			}
		}
	});
	$(document).on('submit', '#note_form', function(event) {
		let form_data = new FormData($('#note_form')[0]);
		form_data.append('channel_id', selected_channel);
		event.preventDefault();
		if(selected_channel != null) {
			$.ajax({data: form_data,contentType:false, processData:false, url:'add-note', method:'POST'}).done(function(data) {
				$("#note_form").trigger("reset");
				add_note(data['new_note'], '');
			});
		}
	});
	$(document).on('click','#menulist .classroom',function(){
		let id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10);
		selected_classroom = id;
		$.ajax({url:`retrieve-channels/${id}`, type:'POST'}).done((data) => {
			console.log(data);
			if(data['result'].length > 0){
				let result = '';
				for(let i = 0; i < data['result'].length; i++) {
					result+= `<li id="$${data['result'][i].id}" class='w3-bar-item w3-button' style='text-decoration: none; width:100%'><i class="fas fa-hashtag"></i>${data['result'][i].name}</li>`;
				}
				$('#menulist ul').html('');
				$(this).parent().children('.channels').first().html(result);
			} 
		});
	});
	$(document).on('click', '.classroom i', function() {
		$('#classroom_settings').css('width', '100%');
		let id = parseInt($(this).parent().attr('id').slice(1, $(this).parent().attr('id').length),10);
		$.ajax({url:`classroom-settings/${id}`, type:'POST'}).done(function(data) {
			console.log(data);
			$('#code_id').html(data['room_code']);
			$('#channel_selection').html('<option value=-1>none</option>');
			$('#user_selection').html('<option value=-1>none</option>');
			for(let i = 0; i < data.channels.length;i++) {
				$('#channel_selection').append(`<option value='${data.channels[i].id}'>${data.channels[i].name}</option>`);
			}
			for(let i = 0; i < data.members.length; i++) {
				$('#user_selection').append(`<option value='${data.members[i].id}'>${data.members[i].name}</option>`);
			}
			if(data.permission) {
				$('.permission').show();
			}
			else {
				$('.permission').hide();
			}
		});
	});
	$(document).on('click', '#channels_action_submission_button', function() {
		channel_id = $('#channel_selection').children("option:selected").val();
		socket.emit('channel_action', {'classroom_id': selected_classroom, 'action': $('#action_selection').children("option:selected").html(), 'channel_id': channel_id, 'name_input': $('#name_input').val()});
	});
	$(document).on('click', '#users_action_submission_button', function() {
		user_id = $('#user_selection').children("option:selected").val();
		socket.emit('user_action', {'classroom_id': selected_classroom, 'action': $('#action_selection_users').children("option:selected").html(), 'user_id': user_id});
	});
	$(document).on('change', '#action_selection', function() {
        let selectedAction = $(this).children("option:selected").html();
        if(selectedAction == 'rename' || selectedAction == 'add') {
        	console.log('selected action is rename');
        	$('#name_input').css('display', 'block');
        }
        else {
        	$('#name_input').css('display', 'none');
        }
	});
	$(document).on('click', '.channels li', function() {
		let id = parseInt($(this).attr('id').slice(1, $(this).attr('id').length), 10); //getting channel id
		selected_channel = id;
		set_chat_title($(this).parent().parent().children('a').first().html(),$(this).html());
		$.ajax({url:`retrieve-messages/${id}`, type:'POST'}).done((data) => {
			clear_chatbox()
			if (data.result.length) {
				for(let i=0; i < data.result.length; i++) {
					add_message(data.result[i]);
				}
			} else {
				let message = {'author': {'name': 'SC. Bot'}, 'content': 'No messages to display', 'date': 'just now'};
				add_message(message);
			}
		});
		$.ajax({url:`retrieve-notes/${id}`, type:'POST'}).done((data) => {
			clear_notes();
			if(data.length) {
				for(let i = 0;i < data.length; i++) {
					if(i == 0) {
						add_note(data[i], 'active');
					}
					else {
						add_note(data[i], '');
					}
				}	
			}
			else {
				new_note = {'note_title': 'No data', 'note_text': 'No data', 'note_id': -1};
				add_note(new_note,'active');
			}
		});
		$.ajax({url:`retrieve-assignments/${id}`, type:'POST'}).done((data) => {
			console.log(data);
			clear_assignments();
			if(data.assignments.length) {
				result = false;
				if(data.role == 'super') {
					result = true;
				}
				for(let i = 0; i  < data.assignments.length; i++) {
					add_assignment(data.assignments[i], result);
				}
			}
			else {
				new_assignment = {'text': 'none', 'duedate': 'none', 'submission_state': '.'};
				add_assignment(new_assignment);
			}
		});
	});
	$(document).on('click', '#newconversation', function() {
		$('#new_conversation_form').css('display', 'block'); //showing new conversation form
		$('#newconversation').css('display', 'none'); //hiding newconversation button
	});
	$(document).on('keydown', '#new_conversation_form', function(event) {
		if (event.keyCode == 13) {
			event.preventDefault(); //preventing form from submitting
			const user_input = $('#new_conversation_input').val(); //assigning the input to a variable
			$('#new_conversation_input').val(''); //setting input value to empty string
			if (selected_channel != null) {
				socket.emit('channel_conversation', {'channel_id': selected_channel, 'message': user_input});
			}
		}
	});
	$(document).on('click', '#regenerate_code', function() {
		socket.emit('code_regeneration_req', {'classroom_id': selected_classroom});
	});
	$(document).on('click', '#leave_classroom', function() {
		socket.emit('classroom_leave', {'classroom_id': selected_classroom});
		set_chat_title('', 'No channel to display...');
		clear_notes();
		clear_chatbox();
		close_settings_menu();
		$(`[id='%${selected_classroom}']`).parent().remove();
	});
	$(document).on('submit', "#assignment_form", function(event) {
		event.preventDefault();
		$('#selected_channel_input').val(selected_channel);
		$.ajax({url:'/add-assignment', type:'POST', data: $('#assignment_form').serialize(), success: function(data) {
			add_assignment(data, true);
		}});
	});
	$(document).on('submit', '#homework_submission', function(event) {
		event.preventDefault();
		let form_data = new FormData($('#homework_submission')[0]);
		form_data.append('channel_id', selected_channel);
		form_data.append('assignment_id', parseInt($('#homework_submission').closest('tr').attr('value'), 10));
		event.preventDefault();
		if(selected_channel != null) {
			$.ajax({data: form_data,contentType:false, processData:false, url:'/homework-submit', method:'POST'}).done(function(data) {
				$('#homework_submission').html('Already submitted');
			});
		}
	});
	$(document).on('click', '.show_submission_button', function() {
		id = parseInt($(this).closest('tr').attr('value'), 10);
		console.log(id);
		$.ajax({url:`retrieve-submissions/${id}`, type:'POST'}).done(function(data) {
			clear_submissions();
			$('#submissions').append('<tr><th>Username</th> <th>Homework File</th></tr>');
			for(i = 0; i < data.length; i++) {
				$('#submissions').append(`<tr><td>${data[i].name}</td><td><a href='${data[i].file}' download>Download submission file</a></td></tr>`);
			}
		});
	});
});
socket.on('channel_conversation', function(data) {
	if(data.channel_id == selected_channel) {
		console.log(data);
		add_message(data);
	}
	else {
		//Code for notification goes here
	}
});
socket.on('channel_delete', function(data) {
	if(selected_channel == parseInt(data['id'], 10)) {
		set_chat_title('','No channel to display...');
		clear_notes();
		clear_chatbox();
	}
	if(selected_classroom == data['classroom_id']) {
		$(`[id='%${data['classroom_id']}']`).parent().children('ul').children().each(function() {
			if($(this).attr('id') == '$' + String(data['id'])){
				$(this).remove();
				$('#channel_selection').children().each(function() {
					if($(this).val() == parseInt(data['id'], 10)) {
						$(this).remove();
					}
				});
			}
		})
	}
});
socket.on('new_channel', function(data) {
	if(selected_classroom == data['classroom_id']) {
		$(`[id='%${data['classroom_id']}']`).parent().children('ul').append(`<li id="$${data['id']}" class='w3-bar-item w3-button' style='text-decoration: none; width:100%'><i class="fas fa-hashtag"></i>${data['name']}</li>`);
		$('#channel_selection').append(`<option value='${data['id']}'>${data['name']}</option>`);
	}
});
socket.on('channel_rename', function(data) {
	if(selected_classroom == data['classroom_id']) {
		$(`[id='%${data['classroom_id']}']`).parent().children('ul').children().each(function() {
			if($(this).attr('id') == '$' + String(data['id'])) {
				$(this).html('<i class="fas fa-hashtag"></i>' + data['new_name']);
			}
		});
		$('#channel_selection').children().each(function() {
			if($(this).val() == parseInt(data['id'], 10)) {
				$(this).html(data['new_name']);
			}
		});
	}
});
socket.on('code_regeneration', function(data) {
	if(selected_classroom == data['classroom_id']) {
		$('#code_id').html(data['code']);
	}
});
socket.on('user_kick', function(data) {
	console.log(data);
	if(parseInt(data['user_id'], 10) == parseInt($('#user_id').attr('value'), 10)) {
		$(`[id='%${data['classroom_id']}']`).parent().remove();
		if(selected_classroom == data['classroom_id']) {
			set_chat_title('','No channel to display...');
			clear_notes();
			clear_chatbox();
		}
	}
});