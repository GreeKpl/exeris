import React from "react";
import {Modal, Button} from "react-bootstrap";

class NotificationDialogOption extends React.Component {
  constructor(props) {
    super(props);

    this.handleOption = this.handleOption.bind(this);
  }

  handleOption(event) {
    event.preventDefault();
    this.props.handleOption(this.props.option);
  }

  render() {
    return <Button onClick={this.handleOption}>
      {this.props.children}
    </Button>
  }
}

class NotificationDialog extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.isNotificationDialogVisible) { // notification dialog is not visible
      return null;
    }
    return <Modal show={true} onHide={this.props.hideModal} backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>{this.props.title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {this.props.text}
      </Modal.Body>
      <Modal.Footer>
        {this.props.options.map(option =>
          <NotificationDialogOption key={option.get("endpoint")}
                                    option={option}
                                    handleOption={this.props.handleOption}>
            {option.get("name")}
          </NotificationDialogOption>
        )}
      </Modal.Footer>
    </Modal>
  }
}

export default NotificationDialog;
