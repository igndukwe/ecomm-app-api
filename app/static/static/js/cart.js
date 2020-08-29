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

        // output user in the console
        console.log('USER:', user)

        // check if user is authenticated
        if (user == 'AnonymousUser') {
            addCookieItem(productId, action)
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
    })
        .then((response) => {
            return response.json();// get response
        })
        .then((data) => {
            location.reload() // hot reload to refresh page
        });

}

function addCookieItem(productId, action) {

    // output this in the console
    console.log('User is not authenticated')

    if (action == 'add') {
        // cart is in our main.html header
        // if productId does not exist in the cart, set it to 1
        if (cart[productId] == undefined) {
            cart[productId] = { 'quantity': 1 }

        } else {
            // add to the current item if it exists
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove') {
        // product must exist for it to be removed
        cart[productId]['quantity'] -= 1

        // if item is zero, delete the item from cart
        if (cart[productId]['quantity'] <= 0) {
            console.log('Item should be deleted')
            delete cart[productId];
        }
    }
    // output in the console
    console.log('Cart:', cart)

    // reset the cookie to this value 
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload() // hot reload to refresh
}