class Chatbot {
    constructor() {
        this.userLang=null;
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
//            sendButton: document.getElementById('send'),
            voiceButton: document.getElementById('click_to_record'),
            // studentButton: document.getElementById('student'),
            // parentButton: document.getElementById('parent'),
            // facultyButton: document.getElementById('faculty'),
            selectLanguage: document.getElementById('language-select'),
            stopListeningButton: document.getElementById('stop_recording')
        }
        document.getElementById('listening').style.display = 'none';
        document.getElementById('click_to_record').style.display = 'block';
        this.state = false;
        this.messages = [
            {
                name: 'VNR', message: 'Hello! Welcome to VNR VJIET. How may I help you?'
            }
        ];
        this.count = 0;
    }

    display() {
        const {
            openButton,
             chatBox,
//              sendButton,
               voiceButton,
                studentButton, facultyButton, parentButton, selectLanguage, stopListeningButton } = this.args;
        openButton.addEventListener('click', () => this.toggleState(chatBox))
//        sendButton.addEventListener('click', () => this.onSendButton(chatBox))
        voiceButton.addEventListener('click', () => this.onVoiceButton(chatBox))
        stopListeningButton.addEventListener('click', () => this.stopListening(chatBox))
        this.getSuggestions(chatBox);
        this.userLang=selectLanguage.value;
        selectLanguage.addEventListener('change', () => {this.userLang=selectLanguage.value; this.onVoiceButton(chatBox)})
        const node = document.getElementById('convert_text');
        node.addEventListener('keyup', ({ key }) => {
            if (key == 'Enter') {
                this.onSendButton(chatBox);
            }
        });
    }

  

    onVoiceButton(chatbox) {
        var speech = true;
        console.log("User Lang>>"+this.userLang);

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continous = true;
        recognition.lang = this.userLang;

        recognition.addEventListener('result', e => {
            console.log("entered listener");
            const transcript = Array.from(e.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');
            console.log("1>>" + transcript);
            //Auto Translate
            const intermediate_trans = this.translateToEnglish(transcript, "en");
            console.log("2>>>>"+intermediate_trans)
            const translation=this.translateToEnglish(intermediate_trans, "en");
            //Translate ends
            console.log("3>>>>"+translation)
            document.getElementById("convert_text").value = translation;
            this.stopListening(chatbox);
        });
        if (speech == true) {
            document.getElementById('listening').style.display = 'block';
            document.getElementById('click_to_record').style.display = 'none';
//            document.getElementById('send').style.display = 'none';
            recognition.start();
        }
    }

    stopListening(chatbox){
        document.getElementById('listening').style.display = 'none';
        document.getElementById('click_to_record').style.display = 'block';
//        document.getElementById('send').style.display = 'block';
        this.onSendButton(chatbox);
    }

    toggleState(chatbox) {
        this.state = !this.state
        if (this.state) {
            chatbox.classList.add('chatbox--active');
        } else {
            chatbox.classList.remove('chatbox--active');
        }
    }
    getSuggestions(chatbox){
        const url = "/search";
        const request = new XMLHttpRequest();
        request.open('GET', url, false); // synchronous request
        request.send();

        if (request.status === 200)
        {
            const responseText = request.responseText;
            const translation = JSON.parse(responseText);
            if( translation != null && translation.length != 0)
            {
                console.log("Translation ", translation)
                let list_html = "<ol style='margin-left: 15px;'>"
                for(var i=0; i<translation.length; i++)
                {
                    const tagAndValue = translation[i].split(";");
                    list_html+="<li><a>"+tagAndValue[0]+" : </a><a target='_blank' href='"+tagAndValue[1]+"'>"+tagAndValue[1]+"</a></li>";
                }
                list_html += "</ol>"
                this.messages.push({ name: 'category', message: "Top "+translation.length+" frequently visited pages <br><br>" + list_html })
                //this.messages.push({ name: 'category', message: ""+ translation[0]})
                this.updateChatText(chatbox)
                return translation;
            }

        }
        else
        {
            console.error('Translation request failed with status', request.status);
            return null;
        }
    }

    onSendButton(chatbox) {
        console.log('clicked send button');
        var textFeild = document.getElementById('convert_text');
        let text1 = textFeild.value;
        console.log('textfield value ' + text1);
        if (text1 === '') {
            return;
        }
        fetch('/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(r => r.json())
            .then(r => {
                let msg2 = { name: "VNR", message: r.answer };
                if(r.query.toLowerCase() != text1.toLowerCase()){
                    text1 += "<br><sub> corrected to: <b>"+r.query+"</b></sub> "
                }
                let msg1 = { name: 'User', message: text1 }

                this.messages.push(msg1);
                this.messages.push(msg2);
                this.updateChatText(chatbox)
                textFeild.value = ''
            })
            .catch((error) => {
                console.error('Errror :', error)
                this.updateChatText(chatbox)
                textFeild.value = '';
            })
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function (item) {
            if (item.name === "VNR") {
                if (item.message == 'Hello! Welcome to VNR VJIET. How may I help you?') {
                    html += '<div class="messages__item message__item--visitor messages__item--visitor">' + 'Hello! Welcome to VNR VJIET. How may I help you?' + '</div>';
                }
                else {
                    if (item.message == 'I do not understand...') {
                        html += '<div class="messages__item message__item--visitor messages__item--visitor">' + 'We couldn' + "'" + 't find what you were searching for, please try asking in another way / an appropriate question.' + '</div>';
                    }
                    else {
                        if( item.message.includes('://')) {
                            html += '<div class="messages__item message__item--visitor messages__item--visitor">' + 'You can get the required response from the link -' + '<a href="' + item.message + ' " target="_blank">' + item.message + '</a></div>';
                        }
                        else{
                            html += '<div class="messages__item message__item--visitor messages__item--visitor">' + item.message + '</div>';
                        }
                    }
                }
            }
            if (item.name === 'category') {
                html += '<div class="messages__item message__item--visitor messages__item--visitor">' + item.message + '</div>'
            }
            if (item.name === 'User') {
                html += '<div class="messages__item message__item--operator messages__item--operator">' + item.message + '</div>'
            }
        })

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;

        // Opens Url in new tab
        const last_message = this.messages.at(-1).message;
        // if(last_message != null && last_message.includes("://")){
            if(last_message != null && last_message.includes("://") && !last_message.includes("frequently visited pages")){
            console.log("opening in new tab : " + last_message);
                const new_tab = window.open(last_message, '_blank');
                if(new_tab != null){
                    new_tab.focus();
                }
        }
    }

    translateToEnglish(text, targetLanguage) {
      const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=${targetLanguage}&dt=t&q=${encodeURIComponent(text)}`;
      const request = new XMLHttpRequest();
      request.open('GET', url, false); // synchronous request
      request.send();

      if (request.status === 200) {
        const responseText = request.responseText;
        const translation = JSON.parse(responseText)[0][0][0];
        return translation;
      } else {
        console.error('Translation request failed with status', request.status);
        return null;
      }
    }
}

const chatbox = new Chatbot();
chatbox.display();