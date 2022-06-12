function create_payment_div(data) {
    amount = data['amount'].toString();
    document.getElementById('paymentdiv').style.display = "block";
    document.getElementById('amountToPayInfo').innerHTML = amount;
};

function create_error_div(error_msg) {
    document.getElementById('errordiv').style.display = "block";
    document.getElementById('errormsg').innerHTML = error_msg;
};

const getSubscriptionInfoAPIEndpoint = '/api/sub-info';
fetch(getSubscriptionInfoAPIEndpoint)
.then(response=>{return response.json()})
.then(function (response) {
    if (response["available_subscriptions"] <= 0) {
        document.getElementById('substartdate').disabled = true;
        document.getElementById('subenddate').disabled = true;
        document.getElementById('platenum').disabled = true;
        create_error_div('No available subscriptions at the moment.')
    }}).catch(error=>{console.log('Looks like there was a problem: ', error)});

document.getElementById('submitbutton').addEventListener('click', function(e) {
    e.preventDefault();

    const plateNum = document.getElementById('platenum').value;
    const startDate = document.getElementById('substartdate').value;
    const endDate = document.getElementById('subenddate').value;

    const getSubscriptionAPIEndpoint = '/api/subscription';

    fetch(getSubscriptionAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'plate_nr': plateNum, 'start_date': startDate, 'end_date': endDate}),
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

document.getElementById('submitpayment').addEventListener('click', function(e) {
    e.preventDefault();

    const plateNum = document.getElementById('platenum').value;
    const startDate = document.getElementById('substartdate').value;
    const endDate = document.getElementById('subenddate').value;

    const payAPIEndpoint = '/api/pay-sub';

    fetch(payAPIEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'start_date': startDate, 'end_date': endDate, 'plate_nr': plateNum}),
        }).then(function (response) {
            if (response.status != 200){
                console.log(status)
                return response;
            }
            else {
                console.log(response)
                return response.json();
            }
        }).catch(function (error) {
            console.error(error);
        });
    });

document.getElementById('substartdate').addEventListener('change', function(e) {

    const getSubscriptionInfoAPIEndpoint = '/api/sub-info';
    const endDate = document.getElementById('subenddate');
    endDate.min = e.target.value;
    endDate.value = e.target.value;
    let d = new Date(e.target.value);

    fetch(getSubscriptionInfoAPIEndpoint)
    .then(response=>{return response.json()})
    .then(function (response) {
        if (response['max_subscription_time'] < 28) {
            d = new Date(d.getTime() + 1000*3600*24*response['max_subscription_time']);
        }
        else {
            d = new Date(d.getTime() + 1000*3600*24*28);
        }
    })

    let value = d.toISOString().slice(0,10);
    endDate.setAttribute('max', value);

    });
