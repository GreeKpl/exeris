import {connect} from "react-redux";
import Notifications from "./Notifications";
import {
  getCharacterAndPlayerNotifications,
  fromNotificationsState,
  requestMissingNotifications
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
    requestState: () => dispatch(requestMissingNotifications()),
  }
};

const NotificationsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Notifications);

export default NotificationsContainer;
