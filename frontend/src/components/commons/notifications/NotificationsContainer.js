import {connect} from "react-redux";
import {
  getCharacterAndPlayerNotifications,
  fromNotificationsState,
  requestMissingNotifications, requestShowNotification, removeNotification
} from "../../../modules/notifications";
import React from "react";
import {Alert} from "react-bootstrap";
import NotificationDialogContainer from "./NotificationDialogContainer";

class Notification extends React.Component {
  constructor(props) {
    super(props);

    this.handleDisplay = this.handleDisplay.bind(this);
    this.handleDismiss = this.handleDismiss.bind(this);
  }

  render() {
    return <Alert variant={this.props.type === "error" ? "danger" : "info"}
                  onDismiss={this.props.closeable ? this.handleDismiss : null}
                  onClick={this.props.detailed ? this.handleDisplay : null}>
      {this.props.title}
    </Alert>
  }

  handleDisplay() {
    this.props.onDisplay(this.props.id);
  }

  handleDismiss() {
    this.props.onDismiss(this.props.id);
  }
}


class Notifications extends React.Component {
  componentDidMount() {
    this.props.requestState();
  }

  render() {
    return <div style={{
      position: "fixed",
      top: "80px",
      right: "10px",
      width: "400px",
    }}>
      {this.props.notifications.map(notification =>
        <Notification key={notification.get("id")}
                      title={notification.get("title")}
                      id={notification.get("id")}
                      onDisplay={this.props.onDisplay}
                      closeable={notification.get("easyClose")}
                      detailed={notification.get("detailed")}
                      type={notification.get("type")}
                      onDismiss={this.props.onDismiss}
        />
      )}
      <NotificationDialogContainer key="notificationDialog"/>
    </div>
  }

}

export {Notifications};


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    notifications: getCharacterAndPlayerNotifications(
      fromNotificationsState(state), ownProps.characterId),
  };
};


const mapDispatchToProps = (dispatch) => {
  return {
    requestState: () => {
      dispatch(requestMissingNotifications());
    },
    onDisplay: notificationId => {
      dispatch(requestShowNotification(notificationId));
    },
    onDismiss: notificationId => {
      dispatch(removeNotification(notificationId));
    },
  }
};

const NotificationsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Notifications);

export default NotificationsContainer;
