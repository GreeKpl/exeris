import {connect} from "react-redux";
import Notifications from "./Notifications";
import {
  getCharacterAndPlayerNotifications,
  fromNotificationsState,
  requestMissingNotifications, requestShowNotification, removeNotification
} from "../../modules/notifications";

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
