/**
 *
 * @param onEnterCallback which uses its first and only argument as a generic event,
 * because KeyEvent is supplied instead of ClickEvent. It's allowed to perform generic event functions like preventDefault.
 */
export const fireOnEnter = onEnterCallback => event => {
  if (event.key === "Enter") {
    event.preventDefault();
    onEnterCallback(event);
  }
};
