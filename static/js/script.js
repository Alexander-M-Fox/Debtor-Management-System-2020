function currTotalOwed() {
    debtorTags = document.getElementsByClassName("currTotalOwed");
    for (let i = 1; i <= debtorTags.length; i++) {
        let totalOwed = requestTotalOwed(i);
    }
}

currTotalOwed();

function requestTotalOwed(debtorID) {
    var request = new XMLHttpRequest();
    request.open("GET", "/api/currTotalOwed/" + debtorID);
    request.onload = function () {
        if (request.readyState == 4 && request.status == "200") {
            var jReponse = JSON.parse(request.response);
            document.getElementById(
                debtorID
            ).innerHTML = `Current Total Owed: £${request.response}`;
            return request.response;
        } else {
            console.error(JSON.parse(request.responseText));
        }
    };
    request.send();
}
