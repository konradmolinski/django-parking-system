document.getElementById('submitplatenum').addEventListener('click', function(e) {
    e.preventDefault();

    const plateNumberForm = document.getElementById('platenum').value;


    const getTicketAPIEndpoint = '/api/get-ticket';

    fetch(getTicketAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNumberForm}),
        }).then(function (response) {
            if (response.status != 200){
                console.log(status)
            }
            else {
                console.log(response)
                return response
            }
        }).then(function (response) {
            return response.json();
        }).catch(function (error) {
            console.error(error);
        });
    });

function create_payment_div(data) {

    amount = data['amount'].toString();
    document.getElementById('paymentdiv').style.display = "block";
    document.getElementById('amountinfo').innerHTML += amount;
    payEventListener();

};


document.getElementById('submitreturnticket').addEventListener('click', function(e) {
    const ticketIDForm = document.getElementById('ticketid').value;

    e.preventDefault();

    const returnTicketAPIEndpoint = '/api/return-ticket';

    fetch(returnTicketAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'ticket_id': ticketIDForm}),
        }).then(function (response) {
            json = response.json();
            return [response.json(), response.status];
        }).then(function (resp_and_status) {
            data = resp_and_status[0];
            status=resp_and_status[1];
            if (status !== 200){
                document.getElementById("message").innerHTML=data.error_msg;
                return;
            }
            console.log(data['amount']);
            if (data['amount'] > 0){
                create_payment_div(data);
            }
            else{
            document.getElementById("message").innerHTML="Nothing to pay";
            }
        }).catch(function (error) {
            console.error(error);
            document.getElementById("message").innerHTML=error;
        });
    });

function payEventListener() {
    document.getElementById('submitpayment').addEventListener('click', function(e) {
        e.preventDefault();

        const payAPIEndpoint = '/api/pay';

        fetch(payAPIEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'payment_status': 'P', 'ticket_id': document.getElementById('ticketid').value}),
            }).then(function (response) {
                if (response.status != 200){
                    console.log(status)
                }
                else {
                    console.log(response)
                    return response
                }
            }).then(function (response) {
                return response.json();
            }).catch(function (error) {
                console.error(error);
            });
        });
    }