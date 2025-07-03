package tutorial;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.meta.api.objects.Update;
import io.github.cdimascio.dotenv.Dotenv;



public class Bot extends TelegramLongPollingBot {
  private static final Dotenv dotenv = Dotenv.load();

  @Override
  public String getBotUsername() {
      return "WUPHF_Bot";
  }

  @Override
  public String getBotToken() {
       return dotenv.get("TOKEN");
  }

  @Override
  public void onUpdateReceived(Update update) {
    var msg = update.getMessage();
    var user = msg.getFrom();
    var id = user.getId();
    System.out.println(user.getFirstName()+ " wrote " + msg.getText());
    sendText(id, msg.getText());
  }


  public void sendText(Long who, String what) {
    SendMessage sm = SendMessage.builder().chatId(who.toString()).text(what).build();
    try {
      execute(sm);
    } catch(TelegramApiException e) {
      throw new RuntimeException(e);
    }
  }
}