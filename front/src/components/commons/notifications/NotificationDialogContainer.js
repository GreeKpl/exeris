import {connect} from "react-redux";
import NotificationDialog from "./NotificationDialog";
import {
  getVisibleNotification,
  fromNotificationsState,
  selectNotificationOption,
  hideNotificationDialog
} from "../../../modules/notifications";

const mapStateToProps = (state, ownProps) => {
  const visibleNotification = getVisibleNotification(fromNotificationsState(state));

  return {
    characterId: ownProps.characterId,
    isNotificationDialogVisible: visibleNotification.size > 0,
    text: visibleNotification.get("text"),
    options: visibleNotification.get("options"),
  };
};


const mapDispatchToProps = (dispatch) => {
  return {
    hideModal: () => {
      dispatch(hideNotificationDialog());
    },
    handleOption: option => {
      dispatch(selectNotificationOption(option.toJS()));
    }
  }
};

const NotificationDialogContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(NotificationDialog);

export default NotificationDialogContainer;
