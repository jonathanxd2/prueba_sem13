package utec.dbp.mychat;

import android.app.Activity;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import org.json.JSONException;
import org.json.JSONObject;

public class ChatActivity extends AppCompatActivity {
    public static final String EXTRA_USER_ID = "userID";
    public static final String TAG = "ChatActivity";

    RecyclerView mRecyclerView;
    RecyclerView.Adapter mAdapter;

    public Activity getActivity() {
        return this;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);
        mRecyclerView = findViewById(R.id.main_recycler_view);
    }

    @Override
    protected void onResume() {
        super.onResume();

        mRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        String userId = getIntent().getExtras().get(EXTRA_USER_ID).toString();
        String url = "http://10.0.2.2:5000/chats/"+userId;
        RequestQueue queue = Volley.newRequestQueue(this);

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(
            Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                @Override
                public void onResponse(JSONObject response) {
                    try {
                        mAdapter = new MyAdapter(response.getJSONArray("response"),getActivity());
                        mRecyclerView.setAdapter(mAdapter);
                    } catch (JSONException e) {
                        Log.d(TAG, e.getMessage());
                    }
                }
            }, new Response.ErrorListener() {

                 @Override
                 public void onErrorResponse(VolleyError error) {
                    Log.d(TAG, error.getMessage());
                  }
            }
        );
        queue.add(jsonObjectRequest);
    }
}