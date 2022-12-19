document.addEventListener('DOMContentLoaded', () => {

  function compose_email() {
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    cleanCompositionForm();
  }


  /********************
  *  HELPER FUNCTIONS *
  ********************/

  const cleanCompositionForm = () => {
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }


  const load_mailbox = async (mailbox) =>  {

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    emails = await getMailbox(mailbox);
    printEmails(emails);
  }


  const getMailbox = async (mailbox) => {
    const promise = fetch(`/emails/${mailbox}`)
    .then(response => response.json());

    const emails = await promise;
    return emails;
  }


  const sendMail = () => {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
      })
    })
    .then(response => response.json())
    .then(result => {
      if(result.error) {
        showMessage('Error', result.error, 'error');
        return;
      }

      showMessage('Success', result.message, 'success');
      load_mailbox('sent');
    });
  }


  const printEmails = (emails) => {
    emails.forEach(email => {
      const emailDiv = document.createElement('div');
      emailDiv.id = `email-container-${email.id}`;

      const emailContainer = document.createElement('div');
      emailContainer.className = 'card';

      const cardHeader = document.createElement('div');
      cardHeader.id = `email-header-${email.id}`;
      cardHeader.className = `card-header ${email.read ? 'bg-secondary' : 'bg-light'}`;

      const cardTitle = document.createElement('h2');
      cardTitle.className = 'mb-0';

      const cardButton = document.createElement('button');
      cardButton.className = `btn ${email.read ? 'btn-secondary' : 'btn-light'} w-100 d-flex justify-content-between`;
      cardButton.type = 'button';
      cardButton.innerHTML = `<span>To: ${email.recipients[0]} ${email.recipients.length > 1 ? `+${email.recipients.length - 1} more` : ''}</span> <span>${email.subject}</span> <span class="badge ${email.read ? 'badge-secondary' : 'badge-light'}">${email.timestamp}</span>`;

      const cardButton2 = document.createElement('button');
      cardButton2.className = `btn ${email.archived ? 'btn-primary' : 'btn-danger'}`;
      cardButton2.id = 'change-archived-status-btn';
      cardButton2.innerHTML = `${email.archived ? 'Unarchive' : 'Archive'}`;
      cardButton2.addEventListener('click', (e) => {
        e.stopPropagation();
        updateArchivedStatus(email.id, !email.archived);
      });

      cardButton.append(cardButton2);
      cardTitle.append(cardButton);
      cardHeader.append(cardTitle);
      emailContainer.append(cardHeader);
      emailDiv.append(emailContainer);

      document.querySelector('#emails-view').append(emailDiv);
      emailDiv.addEventListener('click',  (e) => { viewEmail(email.id) });
    });
  }


  const updateArchivedStatus = async (emailId, newStatus) => {
    await fetch(`/emails/${emailId}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: newStatus
      })
    });

    load_mailbox('inbox');
  }


  const viewEmail = async (emailId) => {
    // Mark email as read
    fetch (`/emails/${emailId}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      })
    });

    const email = await getEmail(emailId);
    const emailDiv = document.querySelector(`#email-view`);
    const emailContainer = document.createElement('div');
    emailContainer.className = 'card';

    const emailCard = document.createElement('div');
    emailCard.className = 'card-header';
    emailCard.id = `email-header-${email.id}`;
    emailCard.innerHTML = `
                          <h2 class="mb-0">
                            <button class="btn btn-link w-100 d-flex justify-content-between" type="button">
                              From: ${email.sender} <span class="badge badge-secondary">${email.timestamp}</span>
                            </button>
                          </h2>
                          <h4 class="card-title">Subject: ${email.subject}</h4>
                          <h5 class="card-subtitle mb-2 text-muted">To: ${email.recipients.join(', ')}</h5>
                          <hr>
                          <p class="card-text">${email.body}</p>
                        `;
    emailContainer.append(emailCard);

    const replyButton = document.createElement('button');
    replyButton.className = 'btn btn-primary';
    replyButton.id = 'reply-btn';
    replyButton.innerHTML = 'Reply';
    replyButton.addEventListener('click', () => { replyEmail(email) });
    emailCard.append(replyButton);

    emailDiv.replaceChildren();
    emailDiv.append(emailContainer);
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';
  }


  const replyEmail = (email) => {
    const replyDiv = document.querySelector(`#compose-recipients`);
    replyDiv.value = email.sender;
    const replySubject = document.querySelector(`#compose-subject`);
    replySubject.value = `Re: ${email.subject}`;
    const replyBody = document.querySelector(`#compose-body`);
    replyBody.value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;

    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
  }


  const getEmail = async (emailId) => {
    return await fetch(`/emails/${emailId}`)
      .then(response => response.json())
  }


  const showMessage = (title, message, icon) => {
    swal({
      title: title,
      text: message,
      icon: icon,
      button: "Ok",
    })
  };


  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#submit-btn').addEventListener('click', sendMail);

  // By default, load the inbox
  load_mailbox('inbox');

});// DOMLoaded
