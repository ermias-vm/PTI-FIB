package mypackage;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import jakarta.servlet.*;
import jakarta.servlet.http.*;

public class CarRentalList extends HttpServlet {

  int cont = 0;

  public void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
    res.setContentType("text/html");
    PrintWriter out = res.getWriter();

    // Obtenir credencials de l'usuari
    String user = req.getParameter("userid");
    String pw = req.getParameter("password");

    if (authenticate(user, pw)) {
      cont++;
      out.println("<html><head><title>Rental List</title></head><body>");
      out.println("<big>Hola Amic " + user + "</big><br>" + cont + " Accesos des de la seva càrrega.<br><br>");
      out.println("<a href='carrental_home.html'>Home</a><br>");
      out.println("<h1>Rentals List:</h1>");

      llegirIImprimirRentals(out, getServletContext());
      out.println("</body></html>");
    } else {
      out.println("<a href='carrental_form_list.html'>List rentals</a><br><br>");
      out.println("<html><span style='color: red;'>Usuari o contrasenya incorrectes.</span></html>");
    }
  }


  private boolean authenticate(String user, String password) {
    return "admin".equals(user) && "admin".equals(password);
  }

  // Funció per llegir els rentals i imprimir-los
  private void llegirIImprimirRentals(PrintWriter out, ServletContext context) {
    // Ruta del fitxer JSON on es registren els rentals
    //String filePath = "/home/ervm/Documents/PTI/lab/ptiBASE/servlets/apache-tomcat-10.0.10/webapps/my_webapp/rentals.json";
    
    String appRootPath = context.getRealPath("/");
    String filePath = appRootPath + "rentals.json";

    File file = new File(filePath);

    if (!file.exists() || file.length() == 0) {
      out.println("<p style='color: red;'>No s'han trobat rentals.</p>");
    } else {
      try (BufferedReader br = new BufferedReader(new FileReader(file))) {
        String line;
        JSONParser parser = new JSONParser();
        while ((line = br.readLine()) != null) {
          try {
            JSONObject rental = (JSONObject) parser.parse(line);
            printRental(out, rental);
          } catch (ParseException pe) {
            pe.printStackTrace();
            out.println("Error en el parseig de les dades del rental.<br><br>");
          }
        }
      } catch (IOException e) {
        e.printStackTrace();
        out.println("<p>Error llegint el fitxer de rentals.</p>");
      }
    }
  }

  // Funció per imprimir les dades del lloguer de cotxe
  private void printRental(PrintWriter out, JSONObject rental) {
    out.println("co2_rating: " + rental.get("co2_rating") + "<br>");
    out.println("sub_model_vehicle: " + rental.get("sub_model_vehicle") + "<br>");
    out.println("dies_lloguer: " + rental.get("dies_lloguer") + "<br>");
    out.println("num_vehicles: " + rental.get("num_vehicles") + "<br>");
    out.println("descompte: " + rental.get("descompte") + "%<br><br>");
  }

  public void doPost(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
    doGet(req, res);
  }
}
 