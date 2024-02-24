import { useState } from "react"
import { Button } from "react-bootstrap";

export default function BadgerSaleItem(props) {

    const [isIncreaseHovering, setIsIncreasinHovering] = useState(false)
    const [isDecreaseHovering, setIsDecreasingHovering] = useState(false)
    const [quantity, setQuantity] = useState(0);

    const increaseQuantity = () => {
        setQuantity(prev => prev + 1)
    };
    const decreaseQuantity = () => {
        setQuantity(prev => prev > 0 ? prev - 1 : 0)
    };
    const normalItems = {
        border: "1px solid",
        padding: "15px",
        borderRadius: "10px",
        backgroundColor: "mistyrose"
    };
    const featuredStyle = {
        backgroundColor: "salmon",
        color: "white",
        border: "5px solid black",
        padding: "15px",
        borderRadius: "15px",
        fontWeight: "bold",
    }
    const button1 = {
        backgroundColor: isIncreaseHovering ? "grey": "silver"
    }
    const button2 = {
        backgroundColor: isDecreaseHovering ? "grey": "silver"
    }
    return (
       <div style= {props.featured ? featuredStyle : normalItems}>

                <div>
                <h2>{props.name}</h2>
                <p>{props.description}</p>
                <p>{props.price}</p>
                <div>
                    <Button className="inline" onClick={decreaseQuantity} disabled={quantity == 0} style = {button2} onMouseOver = {() => setIsDecreasingHovering(true)}  onMouseLeave = {() => setIsDecreasingHovering(false)} >-</Button >
                    <p className="inline">{quantity}</p>
                    <Button
                    style = {button1}
                    className="inline" onClick={increaseQuantity} 
                    onMouseOver = {() => setIsIncreasinHovering(true)} 
                    onMouseLeave = {() => setIsIncreasinHovering(false)}
                    >+</Button>
                </div>
            </div>
        </div>
    );
}