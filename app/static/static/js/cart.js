// Add event handler for each "Add to Cart" button
//////////////////////////////////////////////////
// get all the elements with class 'update-cart'
// e.g.1. get all buttons from the store.html with class 'update-cart'
// e.g.2. get the icon from the cart.html with class 'update-cart'
var updateBtns = document.getElementsByClassName('update-cart')

//iterate through all the items
for (i = 0; i < updateBtns.length; i++) {
    // add event listener on click for each and
    // set a function to execute on each click
    updateBtns[i].addEventListener('click', function () {
        // this is how to invoke our custom  data-product and data-action 
        // parameters we added in the cart.html
        // custom parameters are appended with data-xxx
        // and invoked with dataset.xxx
        var productId = this.dataset.product
        var action = this.dataset.action
        // display data-product=product.id and data-action=add
        console.log('productId:', productId, 'Action:', action)

        // check if user is authenticated
        console.log('USER:', user)
        if (user == 'AnonymousUser') {
            console.log('User is not authenticated')

        } else {
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...')

    // this is the view mtd we want to send data to
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    }).then((response) => {
        // acknowledgement in json value
        return response.json();
    }).then((data) => {
        // console that response data out
        // this is what our view is sending out to the template
        console.log('Data:', data)
        // reload page so that we can see the changes mage
        location.reload()
    });
}