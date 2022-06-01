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

    let labelTag = document.createElement("label");
    let buttonTag = document.createElement("input");

    labelTag.setAttribute("for", "submitpayment");
    buttonTag.setAttribute("id", "submitpayment");
    buttonTag.setAttribute("type", "submit");
    buttonTag.setAttribute("value", "Pay");

    labelTag.innerHTML = 'Amount to pay: ' + data["amount"].toString();

    document.getElementById("paymentdiv").append(labelTag, buttonTag);

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
            if (response.status != 200){
                console.log(status)
            }
            else {
                console.log(response)
                return response
            }
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            create_payment_div(data);
        }).catch(function (error) {
            console.error(error);
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