import React from "react";
import {Alert} from "react-bootstrap";

const Notification = ({title, id, onClick}) => {
  return <Alert bsStyle="info" onDismiss={() => {
  }} onClick={onClick}>{title}</Alert>
};

class Notifications extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  render() {
    return <div style={{
      position: "fixed",
      top: "50px",
      right: "10px",
      width: "400px",
    }}>
      {this.props.notifications.map(notification =>
        <Notification key={notification.get("id")}
                      title={notification.get("title")}
                      id={notification.get("id")}/>
      )}
    </div>
  }
}

export default Notifications;
