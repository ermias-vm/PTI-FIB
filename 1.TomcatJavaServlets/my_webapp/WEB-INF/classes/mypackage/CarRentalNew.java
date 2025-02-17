package mypackage;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import jakarta.servlet.*;
import jakarta.servlet.http.*;


public class CarRentalNew extends HttpServlet {

  int cont = 0;

  public void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
    res.setContentType("text/html");
    PrintWriter out = res.getWriter();
    cont++;

    String co2Rating = req.getParameter("co2_rating");
    String subModelVehicle = req.getParameter("sub_model_vehicle");
    int diesLloguer = Integer.parseInt(req.getParameter("dies_lloguer"));
    int numVehicles = Integer.parseInt(req.getParameter("num_vehicles"));
    double descompte = Double.parseDouble(req.getParameter("descompte"));

    // Validar valors numerics obtinguts
    String errorMsg = validateFields(diesLloguer, numVehicles, descompte);
    if (!errorMsg.isEmpty()) {
      out.println("<html><head><style>");
      out.println(".error { color: red; }");
      out.println("</style></head><body>");
      out.println("<h4>Error de validación:</h4>"); 
      out.println("<p class='error'>" + errorMsg + "</p>");
      out.println("<a href='carrental_form_new.html'>New rental</a><br>");
      out.println("<a href='carrental_home.html'>Home</a><br>");
      out.println("</body></html>");
      return;
  }
    // Mapear el valor de CO2 (int -> string)
    co2Rating = mapCo2Rating(co2Rating);

    // Crear objete JSON amb els parametres obtinguts
    JSONObject jsonObj = new JSONObject();
    jsonObj.put("co2_rating", co2Rating);
    jsonObj.put("sub_model_vehicle", subModelVehicle);
    jsonObj.put("dies_lloguer", diesLloguer);
    jsonObj.put("num_vehicles", numVehicles);
    jsonObj.put("descompte", descompte);

    // Resposta a la peticio de lloguer
    printHtmlResponse(out, co2Rating, subModelVehicle, diesLloguer, numVehicles, descompte);
    //guardar les dades del lloguer al JSON
    writeRentalToFile(jsonObj);
  }

  private String validateFields(int diesLloguer, int numVehicles, double descompte) {
    String error = "";
    if (descompte < 0 || descompte > 100) error += "<br>El percentatge de descompte ha se ser entre 0 y 100. ";
    if (diesLloguer <= 0) error += "<br>El número de dies de lloguer ha de ser major que 0.";
    if (numVehicles <= 0) error += "<br>El número de vehicles ha de ser major que 0.";
    return error;
  }

  private String mapCo2Rating(String rating) {
    switch (rating) {
      case "54":
        return "Extralow";
      case "82":
        return "Medium";
      case "139":
        return "High";
      default:
        return "Low";
    }
  }

  private void printHtmlResponse(PrintWriter out, String co2Rating, String subModelVehicle, int diesLloguer, int numVehicles, double descompte) {
    out.println(cont + " Accesos desde su carga.<br><br>");
    out.println("<html><body>");
    out.println("<h4>Your new rental has been added successfully!</h4><br>");
    out.println("<h6>co2_rating: " + co2Rating + "</h6>");
    out.println("<h6>sub_model_vehicle: " + subModelVehicle + "</h6>");
    out.println("<h6>dies_lloguer: " + diesLloguer + "</h6>");
    out.println("<h6>num_vehicles: " + numVehicles + "</h6>");
    out.println("<h6>descompte: " + descompte + " %</h6><br>");
    out.println("<a href='carrental_form_new.html'>New rental</a><br>");
    out.println("<a href='carrental_home.html'>Home</a><br>");
    out.println("</body></html>");
  }
  
  private void writeRentalToFile(JSONObject jsonObj) {
    String filePath = "/home/ervm/Documents/PTI/lab/ptiBASE/servlets/apache-tomcat-10.0.10/webapps/my_webapp/rentals.json";
    File file = new File(filePath);

    if (!file.exists()) { // es crea arxiu si no existeix
      try {
        file.createNewFile();
      } catch (IOException e) {
        e.printStackTrace();
      }
    }

    //  afegir una linea amb les dades obtingudes al JSON 
    try (FileWriter fileWriter = new FileWriter(file, true);
         BufferedWriter bufferedWriter = new BufferedWriter(fileWriter)) {
      bufferedWriter.write(jsonObj.toJSONString() + "\n");
      bufferedWriter.flush();
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  public void doPost(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
    doGet(req, res);
  }
}